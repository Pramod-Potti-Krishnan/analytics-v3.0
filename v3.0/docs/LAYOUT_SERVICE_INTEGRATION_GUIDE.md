# Layout Service Integration Guide - Interactive Chart Editor

**Goal**: Enable interactive chart editing in real presentations (L02, L03 slides)

---

## 🎯 The Integration

### Current Flow (Without Editor):
```
User requests presentation
    ↓
Layout Builder calls Analytics Service: "Give me chart HTML"
    ↓
Analytics returns: <canvas>...</canvas>
    ↓
Layout Builder puts HTML in L02/L03 section
    ↓
User sees static chart
```

### New Flow (With Editor):
```
User requests presentation
    ↓
Layout Builder calls Analytics Service: "Give me chart HTML WITH EDITOR"
    ↓
Analytics returns: <div><canvas>...</canvas><button>Edit</button><modal>...</modal><script>...</script></div>
    ↓
Layout Builder puts HTML in L02/L03 section (SAME AS BEFORE!)
    ↓
User sees chart + edit button ✨
```

**The difference**: Just pass `enable_editor=true` and `presentation_id` when requesting chart HTML.

---

## 🔌 Integration Steps

### Step 1: Update Analytics Service API (YOUR TEAM)

**Add new parameters to your chart generation endpoint**:

```python
# File: analytics_microservice_v3/main.py (or your main file)

@app.route('/generate-chart', methods=['POST'])
def generate_chart():
    """
    Generate Chart.js chart HTML.

    Request Body:
    {
        "chart_data": {...},
        "enable_editor": true,  # NEW!
        "presentation_id": "uuid"  # NEW!
    }
    """
    data = request.json

    # Extract new parameters
    enable_editor = data.get('enable_editor', False)
    presentation_id = data.get('presentation_id')

    # Generate chart with editor if requested
    html = generator.generate_line_chart(
        data=data['chart_data'],
        height=600,
        enable_editor=enable_editor,  # Pass it through!
        presentation_id=presentation_id
    )

    return jsonify({
        'success': True,
        'html': html  # This now includes editor if enabled
    })
```

**That's it for your team!** The generator already handles everything.

---

### Step 2: Update Layout Builder Request (LAYOUT TEAM)

**In their code where they call your service**:

```python
# File: layout_builder/presentation_generator.py (or wherever)

def generate_slide_l02(slide_data, presentation_id):
    """Generate L02 slide with chart."""

    # Call analytics service
    response = requests.post('http://analytics-service/generate-chart', json={
        'chart_data': slide_data['chart_data'],
        'enable_editor': True,  # NEW! Enable interactive editor
        'presentation_id': presentation_id  # NEW! Pass presentation ID
    })

    chart_html = response.json()['html']

    # Put HTML in slide (SAME AS BEFORE!)
    slide_html = f"""
    <section data-slide-id="{slide_data['slide_id']}">
        <div class="chart-section">
            {chart_html}
        </div>
    </section>
    """

    return slide_html
```

**Changes Required**:
1. Add `enable_editor: True` to request
2. Pass `presentation_id` from URL/context
3. That's it!

---

### Step 3: Deploy Both Services (BOTH TEAMS)

**Your Team**:
1. Deploy updated analytics service with:
   - Modified `chartjs_generator.py` ✅ (already done)
   - New API routes ✅ (already done)
   - Database model ✅ (already done)

**Layout Team**:
1. Deploy updated layout builder with:
   - Modified request to include new parameters
   - (No other changes needed!)

---

## 🧪 Testing in Real Presentation

### Test Scenario:

**1. Generate Presentation**:
```bash
# Layout Builder receives request
POST /api/presentations/generate
{
    "presentation_id": "test-123",
    "slides": [
        {
            "type": "L02",
            "chart_data": {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "values": [125000, 145000, 178000, 195000],
                "format": "currency"
            }
        }
    ]
}
```

**2. Layout Builder Calls Your Service**:
```bash
# Internally, Layout Builder does:
POST http://analytics-service/generate-chart
{
    "chart_data": {...},
    "enable_editor": true,
    "presentation_id": "test-123"
}
```

**3. Your Service Returns HTML**:
```html
<div class="chart-with-editor" style="position: relative;">
    <canvas id="chart-123">...</canvas>
    <button class="chart-edit-btn" onclick="openEditor()">📊 Edit Data</button>
    <div id="modal-123" class="modal">...</div>
    <script>
        // All the interactive editor JavaScript
    </script>
</div>
```

**4. Layout Builder Puts HTML in Slide**:
```html
<section data-slide-id="slide-l02-1">
    <div class="chart-section">
        <!-- Your HTML goes here -->
        <div class="chart-with-editor">...</div>
    </div>
</section>
```

**5. User Opens Presentation**:
- Sees chart with "Edit Data" button
- Clicks button → modal opens
- Edits data → clicks Save
- Chart updates + saves to YOUR database

---

## 🔄 Full Example with Actual Endpoints

### Your Analytics Service:

```python
# File: analytics_microservice_v3/main.py

from flask import Flask, request, jsonify, Blueprint
from chartjs_generator import ChartJSGenerator
from api.chart_data_routes import chart_data_bp

app = Flask(__name__)

# Register chart data API routes
app.register_blueprint(chart_data_bp)

generator = ChartJSGenerator(theme="professional")

@app.route('/api/analytics/generate-chart', methods=['POST'])
def generate_chart():
    """
    Generate chart HTML with optional interactive editor.

    Request:
    {
        "chart_data": {
            "labels": [...],
            "values": [...],
            "format": "currency"
        },
        "chart_type": "line",
        "enable_editor": true,
        "presentation_id": "uuid"
    }

    Response:
    {
        "success": true,
        "html": "<div>...</div>",
        "chart_id": "line-chart-xyz"
    }
    """
    try:
        data = request.json
        chart_data = data.get('chart_data', {})
        chart_type = data.get('chart_type', 'line')
        enable_editor = data.get('enable_editor', False)
        presentation_id = data.get('presentation_id')

        # Generate appropriate chart type
        if chart_type == 'line':
            html = generator.generate_line_chart(
                data=chart_data,
                height=600,
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif chart_type == 'bar':
            html = generator.generate_bar_chart(
                data=chart_data,
                height=600,
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        # ... other chart types

        return jsonify({
            'success': True,
            'html': html,
            'chart_id': chart_data.get('chart_id', f'{chart_type}-chart-{id(chart_data)}')
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5000)
```

### Layout Builder Calls This:

```python
# File: layout_builder/services/analytics_client.py

import requests

class AnalyticsClient:
    """Client for Analytics Microservice."""

    def __init__(self, base_url='http://analytics-service:5000'):
        self.base_url = base_url

    def generate_chart(self, chart_data, chart_type='line', enable_editor=True, presentation_id=None):
        """
        Generate chart HTML from analytics service.

        Args:
            chart_data: Chart data dict
            chart_type: Type of chart
            enable_editor: Enable interactive editor
            presentation_id: Presentation UUID for data persistence

        Returns:
            HTML string
        """
        response = requests.post(
            f'{self.base_url}/api/analytics/generate-chart',
            json={
                'chart_data': chart_data,
                'chart_type': chart_type,
                'enable_editor': enable_editor,
                'presentation_id': presentation_id
            }
        )

        if response.status_code == 200:
            return response.json()['html']
        else:
            raise Exception(f"Analytics service error: {response.text}")


# Usage in presentation generator:
def build_l02_slide(slide_config, presentation_id):
    """Build L02 slide with chart."""

    analytics = AnalyticsClient()

    # Get chart HTML with editor enabled
    chart_html = analytics.generate_chart(
        chart_data=slide_config['chart_data'],
        chart_type=slide_config.get('chart_type', 'line'),
        enable_editor=True,  # Enable interactive editor!
        presentation_id=presentation_id  # For data persistence!
    )

    # Build slide HTML
    slide_html = f"""
    <section class="slide-l02" data-slide-id="{slide_config['slide_id']}">
        <div class="slide-content">
            <h2>{slide_config.get('title', 'Chart')}</h2>
            <div class="chart-container">
                {chart_html}
            </div>
        </div>
    </section>
    """

    return slide_html
```

---

## 🚀 Deployment Checklist

### Your Analytics Team:

- [ ] Database table `chart_data_edits` created
- [ ] API blueprint registered in Flask app
- [ ] `chartjs_generator.py` updated (✅ done)
- [ ] Service deployed and accessible
- [ ] Test endpoint: `POST /api/analytics/generate-chart`
- [ ] Test endpoint: `POST /api/charts/update-data`
- [ ] Test endpoint: `GET /api/charts/get-data/<id>`

### Layout Builder Team:

- [ ] Analytics client updated to pass new parameters
- [ ] `enable_editor=True` added to chart requests
- [ ] `presentation_id` extracted from URL and passed
- [ ] Service redeployed
- [ ] Test presentation generation

### Testing Together:

- [ ] Layout Builder generates presentation
- [ ] Charts show with "Edit Data" button
- [ ] Clicking button opens modal
- [ ] Editing data updates chart
- [ ] Saving data persists to Analytics database
- [ ] Reopening presentation loads saved data

---

## 🎨 Customization (Optional)

### Enable Editor Only for Specific Users:

```python
# In Layout Builder
def build_l02_slide(slide_config, presentation_id, user_permissions):
    enable_editor = user_permissions.get('can_edit_charts', False)

    chart_html = analytics.generate_chart(
        chart_data=slide_config['chart_data'],
        enable_editor=enable_editor,  # Conditional!
        presentation_id=presentation_id
    )
```

### Enable Editor Only in Edit Mode:

```python
# In Layout Builder
def build_l02_slide(slide_config, presentation_id, mode='view'):
    enable_editor = (mode == 'edit')  # Only in edit mode

    chart_html = analytics.generate_chart(
        chart_data=slide_config['chart_data'],
        enable_editor=enable_editor,
        presentation_id=presentation_id
    )
```

---

## 🔍 Debugging

### If Edit Button Doesn't Appear:

1. Check Analytics service response:
```bash
curl -X POST http://analytics-service:5000/api/analytics/generate-chart \
  -H "Content-Type: application/json" \
  -d '{
    "chart_data": {"labels": ["A"], "values": [1]},
    "enable_editor": true,
    "presentation_id": "test"
  }'
```

Should return HTML with `<button class="chart-edit-btn">`.

2. Check Layout Builder request:
- Is `enable_editor: true` being sent?
- Is `presentation_id` being sent?

3. Check browser console:
- Any JavaScript errors?
- Is Chart.js loaded?
- Is modal HTML present in DOM?

### If Modal Doesn't Open:

1. Check browser console for errors
2. Verify JavaScript initialized (check for `initChart_` function)
3. Check if modal HTML is in DOM (search for `modal-chart-id`)

### If Save Doesn't Work:

1. Check network tab - is API call being made?
2. Check API response - any errors?
3. Check database - is data being saved?

```bash
# Test API directly
curl -X POST http://analytics-service:5000/api/charts/update-data \
  -H "Content-Type: application/json" \
  -d '{
    "chart_id": "test-chart",
    "presentation_id": "test-pres",
    "labels": ["A", "B"],
    "values": [10, 20]
  }'
```

---

## 📊 Expected Result

### When Everything is Working:

**User opens presentation** →
- Sees chart with data labels and axes
- Sees "📊 Edit Data" button top-right

**User clicks "Edit Data"** →
- Modal popup appears
- Shows current data in editable table
- Has "Add Row" and "Delete" buttons

**User edits data, clicks "Save & Update"** →
- Modal closes
- Chart updates with new data
- Success message appears
- Data saved to database

**User refreshes page** →
- Chart shows updated data (loaded from database)

---

**Status**: 🎯 **READY FOR LAYOUT BUILDER INTEGRATION**

**Next Step**: Layout Builder team adds two parameters to their analytics service call, redeploys, and it works!
