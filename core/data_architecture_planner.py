"""
Data Architecture Planner for Analytics Microservice v1.0.0

LLM-based generation and fallback schemas for DATA_ARCHITECTURE endpoint.
Transforms natural language prompts into ER diagram specifications.

v1.0.0 Initial Release:
- LLM prompt template for ER diagram generation
- Keyword-based fallback schema selection
- Pre-built schemas for common domains (ecommerce, blog, auth, analytics)
- Validation and normalization of generated schemas
"""

import logging
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from models.data_architecture_atomic_models import (
    DataEntity,
    DataField,
    DataRelationship,
    EntityType,
    CardinalityType
)
from settings import settings

logger = logging.getLogger(__name__)


@dataclass
class DataArchitecturePlanRequest:
    """Input for the planner."""
    prompt: str


@dataclass
class DataArchitecturePlanResult:
    """Output from the planner."""
    entities: List[DataEntity] = field(default_factory=list)
    relationships: List[DataRelationship] = field(default_factory=list)
    reasoning: Optional[str] = None
    title: Optional[str] = None


class DataArchitecturePlanner:
    """
    Generate ER diagram specifications from natural language.

    Supports two modes:
    1. LLM Generation: Uses OpenAI to interpret prompts
    2. Fallback Schemas: Pre-built schemas for common domains
    """

    # Fallback schema keywords
    FALLBACK_KEYWORDS = {
        "ecommerce": ["ecommerce", "e-commerce", "shop", "store", "order", "product", "cart", "checkout", "inventory", "shipping"],
        "blog": ["blog", "cms", "content", "post", "article", "comment", "author", "publish"],
        "auth": ["auth", "authentication", "login", "user", "permission", "role", "session", "oauth", "password"],
        "analytics": ["analytics", "event", "metric", "tracking", "pageview", "session", "funnel"],
        "social": ["social", "follow", "friend", "message", "chat", "notification", "feed"],
        "crm": ["crm", "customer", "lead", "contact", "deal", "pipeline", "sales"]
    }

    def __init__(self):
        """Initialize the planner."""
        self.llm_client = None

    async def plan(self, request: DataArchitecturePlanRequest) -> DataArchitecturePlanResult:
        """
        Generate ER diagram specification from prompt.

        Args:
            request: DataArchitecturePlanRequest with prompt

        Returns:
            DataArchitecturePlanResult with entities and relationships
        """
        prompt_lower = request.prompt.lower()

        # Try LLM generation first
        try:
            result = await self._generate_with_llm(request.prompt)
            if result.entities:
                return result
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}, falling back to templates")

        # Fall back to keyword-based templates
        return self._get_fallback_schema(prompt_lower)

    def get_placeholder_schema(self, prompt: Optional[str] = None) -> DataArchitecturePlanResult:
        """
        Get a fallback schema without LLM call (placeholder mode).

        Args:
            prompt: Optional prompt for keyword matching

        Returns:
            DataArchitecturePlanResult with template schema
        """
        if prompt:
            return self._get_fallback_schema(prompt.lower())
        return self._get_basic_schema()

    async def _generate_with_llm(self, prompt: str) -> DataArchitecturePlanResult:
        """Generate ER diagram using LLM."""
        try:
            import openai
            client = openai.AsyncOpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url
            )

            system_prompt = self._get_llm_system_prompt()
            user_prompt = f"USER REQUEST: {prompt}"

            response = await client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            return self._parse_llm_response(content)

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise

    def _get_llm_system_prompt(self) -> str:
        """Get the system prompt for LLM generation."""
        return '''You are a database architect designing an Entity-Relationship (ER) diagram.

Generate a JSON response with this exact structure:
{
  "title": "Schema title",
  "reasoning": "Brief explanation of design decisions",
  "entities": [
    {
      "id": "ent_1",
      "name": "table_name",
      "type": "table",
      "fields": [
        {
          "name": "field_name",
          "data_type": "VARCHAR(255)",
          "is_primary_key": false,
          "is_foreign_key": false,
          "is_nullable": true,
          "default_value": null,
          "references": null
        }
      ],
      "x_position": 20,
      "y_position": 30,
      "description": "Table purpose"
    }
  ],
  "relationships": [
    {
      "id": "rel_1",
      "from_entity": "ent_1",
      "from_field": "foreign_key_field",
      "to_entity": "ent_2",
      "to_field": "id",
      "cardinality": "many_to_one",
      "is_optional": false,
      "label": "relationship name"
    }
  ]
}

DESIGN GUIDELINES:
1. Use proper normalization (3NF minimum)
2. Include created_at, updated_at TIMESTAMP fields on main tables
3. Use appropriate data types:
   - INT for auto-increment IDs
   - UUID for distributed IDs
   - VARCHAR(n) for strings with length limit
   - TEXT for long text
   - TIMESTAMP for dates/times
   - DECIMAL(p,s) for money
   - BOOLEAN for flags
4. Every table needs a primary key (usually 'id')
5. Define clear foreign keys with references
6. Position entities to minimize crossing lines:
   - Main entities toward center (40-60% position)
   - Related entities around them
   - Junction tables between their parents
7. Use snake_case for table and field names
8. Entity types: "table" (default), "view", "enum", "junction"
9. Cardinality options: "one_to_one", "one_to_many", "many_to_one", "many_to_many", "zero_or_one", "zero_or_many"

Generate a complete, normalized schema based on the user's request.'''

    def _parse_llm_response(self, content: str) -> DataArchitecturePlanResult:
        """Parse LLM JSON response into structured result."""
        try:
            data = json.loads(content)

            entities = []
            entity_id_map = {}  # Map original IDs to new IDs

            for i, ent_data in enumerate(data.get("entities", [])):
                original_id = ent_data.get("id", f"ent_{i+1}")

                fields = []
                for fld_data in ent_data.get("fields", []):
                    field = DataField(
                        name=fld_data.get("name", "unknown"),
                        data_type=fld_data.get("data_type", "VARCHAR(255)"),
                        is_primary_key=fld_data.get("is_primary_key", False),
                        is_foreign_key=fld_data.get("is_foreign_key", False),
                        is_nullable=fld_data.get("is_nullable", True),
                        default_value=fld_data.get("default_value"),
                        references=fld_data.get("references")
                    )
                    fields.append(field)

                entity = DataEntity(
                    name=ent_data.get("name", f"table_{i+1}"),
                    type=ent_data.get("type", "table"),
                    fields=fields,
                    x_position=float(ent_data.get("x_position", 20 + (i * 25) % 60)),
                    y_position=float(ent_data.get("y_position", 15 + (i * 20) % 70)),
                    description=ent_data.get("description")
                )
                entities.append(entity)
                entity_id_map[original_id] = entity.id

            relationships = []
            for j, rel_data in enumerate(data.get("relationships", [])):
                from_entity = entity_id_map.get(
                    rel_data.get("from_entity"),
                    rel_data.get("from_entity")
                )
                to_entity = entity_id_map.get(
                    rel_data.get("to_entity"),
                    rel_data.get("to_entity")
                )

                rel = DataRelationship(
                    from_entity=from_entity,
                    from_field=rel_data.get("from_field", "id"),
                    to_entity=to_entity,
                    to_field=rel_data.get("to_field", "id"),
                    cardinality=rel_data.get("cardinality", "one_to_many"),
                    is_optional=rel_data.get("is_optional", False),
                    label=rel_data.get("label")
                )
                relationships.append(rel)

            return DataArchitecturePlanResult(
                entities=entities,
                relationships=relationships,
                reasoning=data.get("reasoning"),
                title=data.get("title")
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise ValueError("Invalid JSON response from LLM")

    def _get_fallback_schema(self, prompt_lower: str) -> DataArchitecturePlanResult:
        """Get appropriate fallback schema based on keywords."""
        # Check each domain's keywords
        for domain, keywords in self.FALLBACK_KEYWORDS.items():
            if any(kw in prompt_lower for kw in keywords):
                method_name = f"_get_{domain}_schema"
                method = getattr(self, method_name, None)
                if method:
                    return method()

        # Default to basic schema
        return self._get_basic_schema()

    def _get_basic_schema(self) -> DataArchitecturePlanResult:
        """Get a basic 3-table schema."""
        users = DataEntity(
            name="users",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="email", data_type="VARCHAR(255)", is_nullable=False),
                DataField(name="name", data_type="VARCHAR(100)", is_nullable=False),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()"),
                DataField(name="updated_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=20.0,
            y_position=30.0,
            description="System users"
        )

        posts = DataEntity(
            name="posts",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="user_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="title", data_type="VARCHAR(200)", is_nullable=False),
                DataField(name="content", data_type="TEXT"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=50.0,
            y_position=30.0,
            description="User posts"
        )

        comments = DataEntity(
            name="comments",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="post_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="posts.id"),
                DataField(name="user_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="content", data_type="TEXT", is_nullable=False),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=80.0,
            y_position=30.0,
            description="Post comments"
        )

        relationships = [
            DataRelationship(
                from_entity=posts.id,
                from_field="user_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="authored by"
            ),
            DataRelationship(
                from_entity=comments.id,
                from_field="post_id",
                to_entity=posts.id,
                to_field="id",
                cardinality="many_to_one",
                label="belongs to"
            ),
            DataRelationship(
                from_entity=comments.id,
                from_field="user_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="written by"
            )
        ]

        return DataArchitecturePlanResult(
            entities=[users, posts, comments],
            relationships=relationships,
            reasoning="Basic content management schema with users, posts, and comments",
            title="Basic Content Schema"
        )

    def _get_ecommerce_schema(self) -> DataArchitecturePlanResult:
        """Get e-commerce schema."""
        users = DataEntity(
            name="users",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="email", data_type="VARCHAR(255)", is_nullable=False),
                DataField(name="password_hash", data_type="VARCHAR(255)", is_nullable=False),
                DataField(name="name", data_type="VARCHAR(100)", is_nullable=False),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()"),
                DataField(name="updated_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=15.0,
            y_position=20.0,
            description="Registered customers"
        )

        categories = DataEntity(
            name="categories",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="name", data_type="VARCHAR(100)", is_nullable=False),
                DataField(name="parent_id", data_type="INT", is_foreign_key=True, references="categories.id"),
                DataField(name="description", data_type="TEXT")
            ],
            x_position=50.0,
            y_position=5.0,
            description="Product categories"
        )

        products = DataEntity(
            name="products",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="category_id", data_type="INT", is_foreign_key=True, references="categories.id"),
                DataField(name="name", data_type="VARCHAR(200)", is_nullable=False),
                DataField(name="description", data_type="TEXT"),
                DataField(name="price", data_type="DECIMAL(10,2)", is_nullable=False),
                DataField(name="stock_quantity", data_type="INT", default_value="0"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=50.0,
            y_position=30.0,
            description="Product catalog"
        )

        orders = DataEntity(
            name="orders",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="user_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="status", data_type="VARCHAR(20)", default_value="'pending'"),
                DataField(name="total_amount", data_type="DECIMAL(10,2)", is_nullable=False),
                DataField(name="shipping_address", data_type="TEXT"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=15.0,
            y_position=55.0,
            description="Customer orders"
        )

        order_items = DataEntity(
            name="order_items",
            type="junction",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="order_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="orders.id"),
                DataField(name="product_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="products.id"),
                DataField(name="quantity", data_type="INT", is_nullable=False),
                DataField(name="unit_price", data_type="DECIMAL(10,2)", is_nullable=False)
            ],
            x_position=50.0,
            y_position=55.0,
            description="Order line items"
        )

        entities = [users, categories, products, orders, order_items]

        relationships = [
            DataRelationship(
                from_entity=categories.id,
                from_field="parent_id",
                to_entity=categories.id,
                to_field="id",
                cardinality="many_to_one",
                is_optional=True,
                label="parent"
            ),
            DataRelationship(
                from_entity=products.id,
                from_field="category_id",
                to_entity=categories.id,
                to_field="id",
                cardinality="many_to_one",
                label="in category"
            ),
            DataRelationship(
                from_entity=orders.id,
                from_field="user_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="placed by"
            ),
            DataRelationship(
                from_entity=order_items.id,
                from_field="order_id",
                to_entity=orders.id,
                to_field="id",
                cardinality="many_to_one",
                label="in order"
            ),
            DataRelationship(
                from_entity=order_items.id,
                from_field="product_id",
                to_entity=products.id,
                to_field="id",
                cardinality="many_to_one",
                label="for product"
            )
        ]

        return DataArchitecturePlanResult(
            entities=entities,
            relationships=relationships,
            reasoning="E-commerce schema with users, categories, products, orders, and order items",
            title="E-Commerce Database Schema"
        )

    def _get_blog_schema(self) -> DataArchitecturePlanResult:
        """Get blog/CMS schema."""
        users = DataEntity(
            name="users",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="email", data_type="VARCHAR(255)", is_nullable=False),
                DataField(name="username", data_type="VARCHAR(50)", is_nullable=False),
                DataField(name="display_name", data_type="VARCHAR(100)"),
                DataField(name="bio", data_type="TEXT"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=10.0,
            y_position=30.0,
            description="Blog authors and readers"
        )

        categories = DataEntity(
            name="categories",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="name", data_type="VARCHAR(100)", is_nullable=False),
                DataField(name="slug", data_type="VARCHAR(100)", is_nullable=False),
                DataField(name="description", data_type="TEXT")
            ],
            x_position=50.0,
            y_position=5.0,
            description="Post categories"
        )

        posts = DataEntity(
            name="posts",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="author_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="category_id", data_type="INT", is_foreign_key=True, references="categories.id"),
                DataField(name="title", data_type="VARCHAR(200)", is_nullable=False),
                DataField(name="slug", data_type="VARCHAR(200)", is_nullable=False),
                DataField(name="content", data_type="TEXT"),
                DataField(name="status", data_type="VARCHAR(20)", default_value="'draft'"),
                DataField(name="published_at", data_type="TIMESTAMP"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=40.0,
            y_position=30.0,
            description="Blog posts/articles"
        )

        tags = DataEntity(
            name="tags",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="name", data_type="VARCHAR(50)", is_nullable=False),
                DataField(name="slug", data_type="VARCHAR(50)", is_nullable=False)
            ],
            x_position=75.0,
            y_position=5.0,
            description="Post tags"
        )

        post_tags = DataEntity(
            name="post_tags",
            type="junction",
            fields=[
                DataField(name="post_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="posts.id"),
                DataField(name="tag_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="tags.id")
            ],
            x_position=75.0,
            y_position=30.0,
            description="Post-tag associations"
        )

        comments = DataEntity(
            name="comments",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="post_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="posts.id"),
                DataField(name="user_id", data_type="INT", is_foreign_key=True, references="users.id"),
                DataField(name="content", data_type="TEXT", is_nullable=False),
                DataField(name="status", data_type="VARCHAR(20)", default_value="'pending'"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=40.0,
            y_position=60.0,
            description="Post comments"
        )

        entities = [users, categories, posts, tags, post_tags, comments]

        relationships = [
            DataRelationship(
                from_entity=posts.id,
                from_field="author_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="written by"
            ),
            DataRelationship(
                from_entity=posts.id,
                from_field="category_id",
                to_entity=categories.id,
                to_field="id",
                cardinality="many_to_one",
                is_optional=True,
                label="in category"
            ),
            DataRelationship(
                from_entity=post_tags.id,
                from_field="post_id",
                to_entity=posts.id,
                to_field="id",
                cardinality="many_to_one"
            ),
            DataRelationship(
                from_entity=post_tags.id,
                from_field="tag_id",
                to_entity=tags.id,
                to_field="id",
                cardinality="many_to_one"
            ),
            DataRelationship(
                from_entity=comments.id,
                from_field="post_id",
                to_entity=posts.id,
                to_field="id",
                cardinality="many_to_one",
                label="on post"
            ),
            DataRelationship(
                from_entity=comments.id,
                from_field="user_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                is_optional=True,
                label="by user"
            )
        ]

        return DataArchitecturePlanResult(
            entities=entities,
            relationships=relationships,
            reasoning="Blog/CMS schema with posts, categories, tags, and comments",
            title="Blog/CMS Database Schema"
        )

    def _get_auth_schema(self) -> DataArchitecturePlanResult:
        """Get authentication/authorization schema."""
        users = DataEntity(
            name="users",
            type="table",
            fields=[
                DataField(name="id", data_type="UUID", is_primary_key=True, is_nullable=False, default_value="uuid_generate_v4()"),
                DataField(name="email", data_type="VARCHAR(255)", is_nullable=False),
                DataField(name="password_hash", data_type="VARCHAR(255)", is_nullable=False),
                DataField(name="email_verified", data_type="BOOLEAN", default_value="false"),
                DataField(name="is_active", data_type="BOOLEAN", default_value="true"),
                DataField(name="last_login", data_type="TIMESTAMP"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()"),
                DataField(name="updated_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=25.0,
            y_position=25.0,
            description="User accounts"
        )

        roles = DataEntity(
            name="roles",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="name", data_type="VARCHAR(50)", is_nullable=False),
                DataField(name="description", data_type="TEXT")
            ],
            x_position=60.0,
            y_position=10.0,
            description="User roles"
        )

        permissions = DataEntity(
            name="permissions",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="name", data_type="VARCHAR(100)", is_nullable=False),
                DataField(name="resource", data_type="VARCHAR(100)", is_nullable=False),
                DataField(name="action", data_type="VARCHAR(50)", is_nullable=False),
                DataField(name="description", data_type="TEXT")
            ],
            x_position=60.0,
            y_position=40.0,
            description="Permission definitions"
        )

        user_roles = DataEntity(
            name="user_roles",
            type="junction",
            fields=[
                DataField(name="user_id", data_type="UUID", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="role_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="roles.id"),
                DataField(name="granted_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=40.0,
            y_position=10.0,
            description="User-role assignments"
        )

        role_permissions = DataEntity(
            name="role_permissions",
            type="junction",
            fields=[
                DataField(name="role_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="roles.id"),
                DataField(name="permission_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="permissions.id")
            ],
            x_position=75.0,
            y_position=25.0,
            description="Role-permission mappings"
        )

        sessions = DataEntity(
            name="sessions",
            type="table",
            fields=[
                DataField(name="id", data_type="UUID", is_primary_key=True, is_nullable=False, default_value="uuid_generate_v4()"),
                DataField(name="user_id", data_type="UUID", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="token_hash", data_type="VARCHAR(255)", is_nullable=False),
                DataField(name="ip_address", data_type="VARCHAR(45)"),
                DataField(name="user_agent", data_type="TEXT"),
                DataField(name="expires_at", data_type="TIMESTAMP", is_nullable=False),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=25.0,
            y_position=55.0,
            description="Active sessions"
        )

        entities = [users, roles, permissions, user_roles, role_permissions, sessions]

        relationships = [
            DataRelationship(
                from_entity=user_roles.id,
                from_field="user_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one"
            ),
            DataRelationship(
                from_entity=user_roles.id,
                from_field="role_id",
                to_entity=roles.id,
                to_field="id",
                cardinality="many_to_one"
            ),
            DataRelationship(
                from_entity=role_permissions.id,
                from_field="role_id",
                to_entity=roles.id,
                to_field="id",
                cardinality="many_to_one"
            ),
            DataRelationship(
                from_entity=role_permissions.id,
                from_field="permission_id",
                to_entity=permissions.id,
                to_field="id",
                cardinality="many_to_one"
            ),
            DataRelationship(
                from_entity=sessions.id,
                from_field="user_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="belongs to"
            )
        ]

        return DataArchitecturePlanResult(
            entities=entities,
            relationships=relationships,
            reasoning="Authentication and authorization schema with RBAC pattern",
            title="Auth/RBAC Database Schema"
        )

    def _get_analytics_schema(self) -> DataArchitecturePlanResult:
        """Get analytics/event tracking schema."""
        users = DataEntity(
            name="users",
            type="table",
            fields=[
                DataField(name="id", data_type="UUID", is_primary_key=True, is_nullable=False),
                DataField(name="anonymous_id", data_type="VARCHAR(100)"),
                DataField(name="email", data_type="VARCHAR(255)"),
                DataField(name="first_seen", data_type="TIMESTAMP", default_value="NOW()"),
                DataField(name="last_seen", data_type="TIMESTAMP")
            ],
            x_position=15.0,
            y_position=30.0,
            description="Tracked users"
        )

        sessions = DataEntity(
            name="sessions",
            type="table",
            fields=[
                DataField(name="id", data_type="UUID", is_primary_key=True, is_nullable=False),
                DataField(name="user_id", data_type="UUID", is_foreign_key=True, references="users.id"),
                DataField(name="device_id", data_type="VARCHAR(100)"),
                DataField(name="ip_address", data_type="VARCHAR(45)"),
                DataField(name="user_agent", data_type="TEXT"),
                DataField(name="started_at", data_type="TIMESTAMP", default_value="NOW()"),
                DataField(name="ended_at", data_type="TIMESTAMP")
            ],
            x_position=40.0,
            y_position=15.0,
            description="User sessions"
        )

        events = DataEntity(
            name="events",
            type="table",
            fields=[
                DataField(name="id", data_type="UUID", is_primary_key=True, is_nullable=False),
                DataField(name="session_id", data_type="UUID", is_foreign_key=True, references="sessions.id"),
                DataField(name="user_id", data_type="UUID", is_foreign_key=True, references="users.id"),
                DataField(name="event_type", data_type="VARCHAR(100)", is_nullable=False),
                DataField(name="event_name", data_type="VARCHAR(200)", is_nullable=False),
                DataField(name="properties", data_type="JSONB"),
                DataField(name="timestamp", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=65.0,
            y_position=30.0,
            description="Tracked events"
        )

        page_views = DataEntity(
            name="page_views",
            type="table",
            fields=[
                DataField(name="id", data_type="UUID", is_primary_key=True, is_nullable=False),
                DataField(name="session_id", data_type="UUID", is_foreign_key=True, references="sessions.id"),
                DataField(name="url", data_type="TEXT", is_nullable=False),
                DataField(name="referrer", data_type="TEXT"),
                DataField(name="title", data_type="VARCHAR(500)"),
                DataField(name="time_on_page", data_type="INT"),
                DataField(name="timestamp", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=40.0,
            y_position=55.0,
            description="Page view tracking"
        )

        entities = [users, sessions, events, page_views]

        relationships = [
            DataRelationship(
                from_entity=sessions.id,
                from_field="user_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                is_optional=True,
                label="by user"
            ),
            DataRelationship(
                from_entity=events.id,
                from_field="session_id",
                to_entity=sessions.id,
                to_field="id",
                cardinality="many_to_one",
                is_optional=True,
                label="in session"
            ),
            DataRelationship(
                from_entity=events.id,
                from_field="user_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                is_optional=True,
                label="by user"
            ),
            DataRelationship(
                from_entity=page_views.id,
                from_field="session_id",
                to_entity=sessions.id,
                to_field="id",
                cardinality="many_to_one",
                label="in session"
            )
        ]

        return DataArchitecturePlanResult(
            entities=entities,
            relationships=relationships,
            reasoning="Analytics schema for event tracking with users, sessions, events, and page views",
            title="Analytics/Event Tracking Schema"
        )

    def _get_social_schema(self) -> DataArchitecturePlanResult:
        """Get social network schema."""
        users = DataEntity(
            name="users",
            type="table",
            fields=[
                DataField(name="id", data_type="UUID", is_primary_key=True, is_nullable=False),
                DataField(name="username", data_type="VARCHAR(50)", is_nullable=False),
                DataField(name="email", data_type="VARCHAR(255)", is_nullable=False),
                DataField(name="display_name", data_type="VARCHAR(100)"),
                DataField(name="bio", data_type="TEXT"),
                DataField(name="avatar_url", data_type="TEXT"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=15.0,
            y_position=35.0,
            description="User profiles"
        )

        follows = DataEntity(
            name="follows",
            type="junction",
            fields=[
                DataField(name="follower_id", data_type="UUID", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="following_id", data_type="UUID", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=40.0,
            y_position=15.0,
            description="Follow relationships"
        )

        posts = DataEntity(
            name="posts",
            type="table",
            fields=[
                DataField(name="id", data_type="UUID", is_primary_key=True, is_nullable=False),
                DataField(name="user_id", data_type="UUID", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="content", data_type="TEXT", is_nullable=False),
                DataField(name="media_urls", data_type="JSONB"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=50.0,
            y_position=35.0,
            description="User posts"
        )

        likes = DataEntity(
            name="likes",
            type="junction",
            fields=[
                DataField(name="user_id", data_type="UUID", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="post_id", data_type="UUID", is_foreign_key=True, is_nullable=False, references="posts.id"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=75.0,
            y_position=20.0,
            description="Post likes"
        )

        messages = DataEntity(
            name="messages",
            type="table",
            fields=[
                DataField(name="id", data_type="UUID", is_primary_key=True, is_nullable=False),
                DataField(name="sender_id", data_type="UUID", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="recipient_id", data_type="UUID", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="content", data_type="TEXT", is_nullable=False),
                DataField(name="read_at", data_type="TIMESTAMP"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=40.0,
            y_position=60.0,
            description="Direct messages"
        )

        entities = [users, follows, posts, likes, messages]

        relationships = [
            DataRelationship(
                from_entity=follows.id,
                from_field="follower_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="follower"
            ),
            DataRelationship(
                from_entity=follows.id,
                from_field="following_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="following"
            ),
            DataRelationship(
                from_entity=posts.id,
                from_field="user_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="by user"
            ),
            DataRelationship(
                from_entity=likes.id,
                from_field="user_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one"
            ),
            DataRelationship(
                from_entity=likes.id,
                from_field="post_id",
                to_entity=posts.id,
                to_field="id",
                cardinality="many_to_one"
            ),
            DataRelationship(
                from_entity=messages.id,
                from_field="sender_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="from"
            ),
            DataRelationship(
                from_entity=messages.id,
                from_field="recipient_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="to"
            )
        ]

        return DataArchitecturePlanResult(
            entities=entities,
            relationships=relationships,
            reasoning="Social network schema with users, follows, posts, likes, and messages",
            title="Social Network Schema"
        )

    def _get_crm_schema(self) -> DataArchitecturePlanResult:
        """Get CRM schema."""
        users = DataEntity(
            name="users",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="email", data_type="VARCHAR(255)", is_nullable=False),
                DataField(name="name", data_type="VARCHAR(100)", is_nullable=False),
                DataField(name="role", data_type="VARCHAR(50)", default_value="'sales_rep'"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=10.0,
            y_position=30.0,
            description="CRM users (sales reps)"
        )

        contacts = DataEntity(
            name="contacts",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="owner_id", data_type="INT", is_foreign_key=True, references="users.id"),
                DataField(name="first_name", data_type="VARCHAR(100)", is_nullable=False),
                DataField(name="last_name", data_type="VARCHAR(100)", is_nullable=False),
                DataField(name="email", data_type="VARCHAR(255)"),
                DataField(name="phone", data_type="VARCHAR(50)"),
                DataField(name="company", data_type="VARCHAR(200)"),
                DataField(name="job_title", data_type="VARCHAR(100)"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=40.0,
            y_position=15.0,
            description="Customer contacts"
        )

        deals = DataEntity(
            name="deals",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="owner_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="contact_id", data_type="INT", is_foreign_key=True, references="contacts.id"),
                DataField(name="name", data_type="VARCHAR(200)", is_nullable=False),
                DataField(name="value", data_type="DECIMAL(12,2)"),
                DataField(name="stage", data_type="VARCHAR(50)", default_value="'lead'"),
                DataField(name="probability", data_type="INT", default_value="0"),
                DataField(name="expected_close", data_type="DATE"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=40.0,
            y_position=45.0,
            description="Sales deals/opportunities"
        )

        activities = DataEntity(
            name="activities",
            type="table",
            fields=[
                DataField(name="id", data_type="INT", is_primary_key=True, is_nullable=False),
                DataField(name="user_id", data_type="INT", is_foreign_key=True, is_nullable=False, references="users.id"),
                DataField(name="deal_id", data_type="INT", is_foreign_key=True, references="deals.id"),
                DataField(name="contact_id", data_type="INT", is_foreign_key=True, references="contacts.id"),
                DataField(name="type", data_type="VARCHAR(50)", is_nullable=False),
                DataField(name="subject", data_type="VARCHAR(200)", is_nullable=False),
                DataField(name="notes", data_type="TEXT"),
                DataField(name="due_date", data_type="TIMESTAMP"),
                DataField(name="completed_at", data_type="TIMESTAMP"),
                DataField(name="created_at", data_type="TIMESTAMP", default_value="NOW()")
            ],
            x_position=75.0,
            y_position=30.0,
            description="Sales activities"
        )

        entities = [users, contacts, deals, activities]

        relationships = [
            DataRelationship(
                from_entity=contacts.id,
                from_field="owner_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                is_optional=True,
                label="owned by"
            ),
            DataRelationship(
                from_entity=deals.id,
                from_field="owner_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="owned by"
            ),
            DataRelationship(
                from_entity=deals.id,
                from_field="contact_id",
                to_entity=contacts.id,
                to_field="id",
                cardinality="many_to_one",
                is_optional=True,
                label="with contact"
            ),
            DataRelationship(
                from_entity=activities.id,
                from_field="user_id",
                to_entity=users.id,
                to_field="id",
                cardinality="many_to_one",
                label="by user"
            ),
            DataRelationship(
                from_entity=activities.id,
                from_field="deal_id",
                to_entity=deals.id,
                to_field="id",
                cardinality="many_to_one",
                is_optional=True,
                label="for deal"
            ),
            DataRelationship(
                from_entity=activities.id,
                from_field="contact_id",
                to_entity=contacts.id,
                to_field="id",
                cardinality="many_to_one",
                is_optional=True,
                label="with contact"
            )
        ]

        return DataArchitecturePlanResult(
            entities=entities,
            relationships=relationships,
            reasoning="CRM schema with contacts, deals, and activities",
            title="CRM Database Schema"
        )
