# Interactive Chart Editor - Team Responsibilities

**Feature**: Real-time chart data editing with database persistence
**Date**: 2025-01-15
**Status**: 📋 Ready for Implementation

---

## 🎨 LAYOUT BUILDER TEAM - Frontend Implementation

### Your Scope: Frontend UI & Chart Updates (No Database)

You handle everything the user sees and interacts with in the browser. NO database work.

---

### 1️⃣ Add "Edit Data" Button to Charts

**Where**: `presentation-viewer.html`

**What to Add**:
```html
<!-- Add this CSS to your stylesheet -->
<style>
.chart-edit-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  z-index: 100;
  transition: all 0.2s;
}

.chart-edit-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.05);
}

.chart-container {
  position: relative;
}
</style>
```

**JavaScript to Add**:
The button gets added automatically by the JavaScript class (see step 3).

---

### 2️⃣ Add Modal Popup HTML

**Where**: `presentation-viewer.html` (at the end, before `</body>`)

**What to Add**:
```html
<!-- Chart Data Editor Modal -->
<div id="chart-data-modal" class="modal-overlay" style="display:none;">
  <div class="modal-content">
    <!-- Modal Header -->
    <div class="modal-header">
      <h2>📊 Edit Chart Data</h2>
      <button class="modal-close">&times;</button>
    </div>

    <!-- Modal Body -->
    <div class="modal-body">
      <div class="chart-info">
        <p><strong>Chart:</strong> <span id="modal-chart-name">-</span></p>
        <p><strong>Type:</strong> <span id="modal-chart-type">-</span></p>
      </div>

      <!-- Editable Data Table -->
      <div class="table-container">
        <table id="chart-data-table" class="editable-table">
          <thead>
            <tr>
              <th style="width: 50px;">#</th>
              <th>Label (X-axis)</th>
              <th>Value (Y-axis)</th>
              <th style="width: 80px;">Actions</th>
            </tr>
          </thead>
          <tbody id="data-table-body">
            <!-- Rows populated dynamically by JavaScript -->
          </tbody>
        </table>
      </div>

      <button id="add-row-btn" class="secondary-btn">+ Add Row</button>
    </div>

    <!-- Modal Footer -->
    <div class="modal-footer">
      <button id="cancel-btn" class="secondary-btn">Cancel</button>
      <button id="save-update-btn" class="primary-btn">💾 Save & Update Chart</button>
    </div>
  </div>
</div>
```

**Full CSS**: See `INTERACTIVE_CHART_EDITOR_SPECIFICATION.md` lines 150-325 for complete modal styles.

---

### 3️⃣ Add JavaScript Logic

**Where**: Create new file `static/js/chart-data-editor.js`

**What to Include**: Complete JavaScript class that handles:
- ✅ Adding edit buttons to all charts
- ✅ Opening modal when button clicked
- ✅ Populating table with current chart data
- ✅ Add/delete row functionality
- ✅ Updating Chart.js instance in real-time
- ✅ Calling backend API to save data
- ✅ Closing modal and showing success message

**Full Code**: See `INTERACTIVE_CHART_EDITOR_SPECIFICATION.md` lines 329-679

**Then include it in your HTML**:
```html
<script src="/static/js/chart-data-editor.js"></script>
```

---

### 4️⃣ Load Saved Data When Presentation Opens

**Where**: `presentation-viewer.html` or your existing reveal config

**What to Add**:
```javascript
// Load saved chart data when presentation loads
async function loadPresentationWithChartData(presentationId) {
  try {
    // Call backend API to get saved data
    const response = await fetch(`/api/charts/get-data/${presentationId}`);
    const result = await response.json();

    if (result.success && result.charts.length > 0) {
      // Wait for Reveal.js to be ready
      Reveal.on('ready', () => {
        // Update each chart with saved data
        result.charts.forEach(chartData => {
          const canvas = document.getElementById(chartData.chart_id);
          if (!canvas) return;

          const chart = Chart.getChart(canvas);
          if (!chart) return;

          // Update chart data
          chart.data.labels = chartData.labels;
          if (chart.data.datasets && chart.data.datasets.length > 0) {
            chart.data.datasets[0].data = chartData.values;
          }

          // Re-render
          chart.update();
        });
      });
    }
  } catch (error) {
    console.error('Error loading saved chart data:', error);
    // Fail silently - presentation still works with original data
  }
}

// Call this when page loads
const presentationId = getPresentationIdFromURL(); // Your existing function
loadPresentationWithChartData(presentationId);
```

---

### ✅ Layout Builder Team Summary

**Files to Create**:
1. `static/js/chart-data-editor.js` - New file with complete JavaScript class

**Files to Modify**:
1. `presentation-viewer.html` - Add modal HTML + include script tag
2. `static/css/chart-editor.css` - Add modal and button styles (or add to existing CSS)
3. `reveal-config.js` - Add data loading on presentation load

**What You're Responsible For**:
- ✅ UI elements (button, modal, table)
- ✅ All CSS styling
- ✅ Opening/closing modal
- ✅ Table editing (add/delete rows)
- ✅ Updating Chart.js instance in browser
- ✅ Making API calls to backend (fetch requests)
- ✅ Loading saved data when presentation opens

**What You're NOT Responsible For**:
- ❌ Database schema
- ❌ API endpoints
- ❌ Saving data to database
- ❌ Authentication/authorization

**Timeline**: 3-4 days
- Day 1: Add modal HTML + CSS
- Day 2: Implement JavaScript class
- Day 3: Wire up chart updates
- Day 4: Load saved data on presentation load

---

## 🔧 YOUR BACKEND TEAM - API & Database

### Your Scope: Database & API Endpoints (No Frontend)

You handle storing and retrieving the chart data. NO frontend work.

---

### 1️⃣ Create Database Table

**What to Create**: New table `chart_data_edits`

**SQL Schema**:
```sql
CREATE TABLE chart_data_edits (
    id SERIAL PRIMARY KEY,
    chart_id VARCHAR(255) NOT NULL,
    presentation_id UUID NOT NULL,
    labels JSONB NOT NULL,  -- Array of X-axis labels
    values JSONB NOT NULL,  -- Array of Y-axis values
    chart_type VARCHAR(50),  -- 'line', 'bar', etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),  -- User ID who made the edit

    -- Constraints
    CONSTRAINT unique_chart_per_presentation
        UNIQUE (chart_id, presentation_id),

    -- Foreign key (if presentations table exists)
    FOREIGN KEY (presentation_id)
        REFERENCES presentations(id)
        ON DELETE CASCADE
);

-- Indexes for fast lookup
CREATE INDEX idx_chart_edits_presentation
    ON chart_data_edits(presentation_id);

CREATE INDEX idx_chart_edits_chart
    ON chart_data_edits(chart_id);
```

**SQLAlchemy Model** (if you use SQLAlchemy):
```python
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from extensions import db

class ChartData(db.Model):
    __tablename__ = 'chart_data_edits'

    id = Column(Integer, primary_key=True)
    chart_id = Column(String(255), nullable=False)
    presentation_id = Column(UUID(as_uuid=True), nullable=False)
    labels = Column(JSONB, nullable=False)
    values = Column(JSONB, nullable=False)
    chart_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(255))

    __table_args__ = (
        db.UniqueConstraint('chart_id', 'presentation_id',
                           name='unique_chart_per_presentation'),
    )

    def to_dict(self):
        return {
            'chart_id': self.chart_id,
            'presentation_id': str(self.presentation_id),
            'labels': self.labels,
            'values': self.values,
            'chart_type': self.chart_type,
            'updated_at': self.updated_at.isoformat()
        }
```

---

### 2️⃣ Create API Endpoint: Save Chart Data

**Endpoint**: `POST /api/charts/update-data`

**What It Does**: Saves edited chart data to database

**Request Body**:
```json
{
  "chart_id": "line-chart-abc123",
  "presentation_id": "87e91ebb-f61b-4da9-8fd7-f6e7c189b704",
  "labels": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
  "values": [125000, 145000, 178000, 195000],
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Chart data updated successfully",
  "chart_id": "line-chart-abc123",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Python Implementation**:
```python
from flask import Blueprint, request, jsonify
from datetime import datetime

chart_data_bp = Blueprint('chart_data', __name__)

@chart_data_bp.route('/api/charts/update-data', methods=['POST'])
def update_chart_data():
    """Save edited chart data to database."""
    try:
        data = request.json

        # Validate required fields
        required_fields = ['chart_id', 'presentation_id', 'labels', 'values']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        chart_id = data['chart_id']
        presentation_id = data['presentation_id']
        labels = data['labels']
        values = data['values']

        # Validate data
        if len(labels) != len(values):
            return jsonify({
                'success': False,
                'error': 'Labels and values must have same length'
            }), 400

        # Save to database
        from models import ChartData, db

        # Find existing record or create new
        existing = ChartData.query.filter_by(
            chart_id=chart_id,
            presentation_id=presentation_id
        ).first()

        if existing:
            # Update existing
            existing.labels = labels
            existing.values = values
            existing.updated_at = datetime.utcnow()
        else:
            # Create new
            new_record = ChartData(
                chart_id=chart_id,
                presentation_id=presentation_id,
                labels=labels,
                values=values,
                updated_at=datetime.utcnow()
            )
            db.session.add(new_record)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Chart data updated successfully',
            'chart_id': chart_id,
            'updated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        print(f"Error updating chart data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

### 3️⃣ Create API Endpoint: Get Chart Data

**Endpoint**: `GET /api/charts/get-data/<presentation_id>`

**What It Does**: Retrieves all saved chart data for a presentation

**Response**:
```json
{
  "success": true,
  "charts": [
    {
      "chart_id": "line-chart-abc123",
      "labels": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
      "values": [125000, 145000, 178000, 195000],
      "updated_at": "2025-01-15T10:30:00Z"
    },
    {
      "chart_id": "bar-chart-def456",
      "labels": ["Product A", "Product B", "Product C"],
      "values": [35.5, 28.3, 22.1],
      "updated_at": "2025-01-15T11:00:00Z"
    }
  ]
}
```

**Python Implementation**:
```python
@chart_data_bp.route('/api/charts/get-data/<presentation_id>', methods=['GET'])
def get_chart_data(presentation_id):
    """Get all saved chart data for a presentation."""
    try:
        from models import ChartData

        charts = ChartData.query.filter_by(
            presentation_id=presentation_id
        ).all()

        chart_data_list = [
            {
                'chart_id': chart.chart_id,
                'labels': chart.labels,
                'values': chart.values,
                'updated_at': chart.updated_at.isoformat()
            }
            for chart in charts
        ]

        return jsonify({
            'success': True,
            'charts': chart_data_list
        }), 200

    except Exception as e:
        print(f"Error fetching chart data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

### 4️⃣ Register Blueprint

**Where**: Your main Flask app file (e.g., `app.py` or `main.py`)

**What to Add**:
```python
from api.chart_data_routes import chart_data_bp

app.register_blueprint(chart_data_bp)
```

---

### ✅ Backend Team Summary

**Files to Create**:
1. `api/chart_data_routes.py` - New file with API endpoints
2. `models/chart_data.py` - New database model
3. Database migration file - Create table schema

**Files to Modify**:
1. `app.py` - Register new blueprint

**What You're Responsible For**:
- ✅ Database table creation
- ✅ Database model (SQLAlchemy)
- ✅ API endpoint: `POST /api/charts/update-data`
- ✅ API endpoint: `GET /api/charts/get-data/<presentation_id>`
- ✅ Data validation
- ✅ Error handling
- ✅ Database queries (save/retrieve)

**What You're NOT Responsible For**:
- ❌ Modal popup UI
- ❌ Edit button
- ❌ Table editing functionality
- ❌ Chart.js updates
- ❌ Any frontend JavaScript

**Timeline**: 2-3 days
- Day 1: Database schema + migration
- Day 2: API endpoints implementation
- Day 3: Testing and error handling

---

## 🔄 How It Works Together

### User Flow:
1. **User clicks "Edit Data"** → Layout Builder's JavaScript opens modal
2. **User edits data** → Layout Builder's JavaScript handles table editing
3. **User clicks "Save"** → Layout Builder's JavaScript:
   - Updates chart in browser (instant visual feedback)
   - Makes `POST /api/charts/update-data` call → **Backend saves to database**
4. **User closes modal** → Layout Builder's JavaScript closes modal
5. **User refreshes page** → Layout Builder's JavaScript:
   - Makes `GET /api/charts/get-data/<id>` call → **Backend returns saved data**
   - Updates all charts with saved data

---

## 📋 Testing Checklist

### Layout Builder Team Tests:
- [ ] Edit button appears on all charts
- [ ] Modal opens when button clicked
- [ ] Table populates with current chart data
- [ ] Can edit X-axis labels
- [ ] Can edit Y-axis values
- [ ] Can add new rows
- [ ] Can delete rows
- [ ] Chart updates immediately when clicking "Save"
- [ ] Modal closes after save
- [ ] Success message appears
- [ ] Cancel button discards changes
- [ ] Saved data loads when presentation reopens

### Backend Team Tests:
- [ ] Database table created successfully
- [ ] `POST /api/charts/update-data` accepts valid data
- [ ] `POST /api/charts/update-data` rejects invalid data
- [ ] Data saves to database correctly
- [ ] Can update existing chart data
- [ ] Can create new chart data record
- [ ] `GET /api/charts/get-data/<id>` returns correct data
- [ ] JSONB columns store arrays correctly
- [ ] Unique constraint works (one record per chart per presentation)
- [ ] Foreign key cascade deletes work

---

## 🚀 Deployment Coordination

### Step 1: Backend Deploy First
**Backend team** deploys:
- Database migration
- API endpoints

**Verify**: API endpoints working via Postman/curl

### Step 2: Frontend Deploy Second
**Layout Builder team** deploys:
- Modal HTML
- CSS
- JavaScript

**Verify**: Can edit charts and data persists

---

## 📞 Points of Contact

### Layout Builder Questions:
- Modal not opening?
- Chart not updating?
- Button positioning issues?
→ Layout Builder team handles

### Backend Questions:
- API returning errors?
- Data not saving?
- Database schema issues?
→ Backend team handles

---

## ⏱️ Overall Timeline

**Week 1**:
- Days 1-2: Backend creates database + API
- Days 3-4: Layout Builder creates UI + JavaScript
- Day 5: Integration testing

**Week 2**:
- Days 1-2: Fix bugs, polish UI
- Day 3: Final testing
- Days 4-5: Deploy to production

**Total**: 1-2 weeks

---

## 📚 Reference Documents

**Full specification**: `INTERACTIVE_CHART_EDITOR_SPECIFICATION.md`
**Working demo**: `chart_editor_demo.html` (open in browser to see it working)

---

**Status**: ✅ Both teams have clear responsibilities - Ready to start implementation!
