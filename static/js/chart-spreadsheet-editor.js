/**
 * Chart Spreadsheet Editor - Excel-like data editor for charts
 * Version: 1.0.0
 *
 * Provides an Excel-like interface for editing chart data with:
 * - Dynamic column configuration per chart type
 * - Cell editing with keyboard navigation (arrows, tab, enter)
 * - Add/delete rows and columns
 * - Copy/paste support from Excel
 * - Active data column highlighting
 * - Data validation
 * - Real-time chart updates
 */

class ChartSpreadsheetEditor {
    constructor(chartId, chartType, initialData, options = {}) {
        this.chartId = chartId;
        this.safeChartId = chartId.replace(/-/g, '_').replace(/\./g, '_').replace(/ /g, '_');
        this.chartType = chartType;
        this.data = this._parseData(initialData);
        this.options = {
            onSave: options.onSave || this._defaultSaveHandler,
            onCancel: options.onCancel || this._defaultCancelHandler,
            apiEndpoint: options.apiEndpoint || '/api/charts/update-data',
            ...options
        };

        this.currentCell = null;
        this.clipboard = null;
        this.originalData = JSON.parse(JSON.stringify(this.data));
        this.columnConfig = this._getColumnConfig();

        // Excel-style selection state
        this.selectedColumn = null;
        this.selectedRow = null;

        this._initializeEventListeners();
    }

    /**
     * Parse incoming data to internal table format
     */
    _parseData(data) {
        const chartType = this.chartType;

        // Auto-detect multi-series format (labels + datasets) regardless of chart type
        // This handles cases where chartType is 'bar' but data is actually multi-series
        if (data && data.labels && Array.isArray(data.labels) &&
            data.datasets && Array.isArray(data.datasets) && data.datasets.length > 0) {
            console.log('🔍 Auto-detected multi-series data format');
            return this._parseMultiSeriesData(data);
        }

        // Handle different data formats by chart type
        if (chartType === 'scatter') {
            return this._parseScatterData(data);
        } else if (chartType === 'bubble') {
            return this._parseBubbleData(data);
        } else if (['bar_grouped', 'bar_stacked', 'area_stacked'].includes(chartType)) {
            return this._parseMultiSeriesData(data);
        } else if (chartType === 'd3_sankey') {
            return this._parseSankeyData(data);
        } else if (chartType === 'd3_choropleth_usa') {
            return this._parseChoroplethData(data);
        } else {
            return this._parseSimpleData(data);
        }
    }

    _parseSimpleData(data) {
        // Label-value format
        if (Array.isArray(data)) {
            return data.map((item, idx) => ({
                id: `row-${idx}`,
                Label: item.label || item.Label || '',
                Value: item.value || item.Value || 0
            }));
        }
        return [];
    }

    _parseScatterData(data) {
        // X-Y format (no labels in table)
        if (Array.isArray(data)) {
            return data.map((item, idx) => ({
                id: `row-${idx}`,
                X: item.x || item.X || 0,
                Y: item.y || item.Y || 0
            }));
        }
        return [];
    }

    _parseBubbleData(data) {
        // Label, X, Y, Radius format
        if (Array.isArray(data)) {
            return data.map((item, idx) => ({
                id: `row-${idx}`,
                Label: item.label || item.Label || `Point ${idx + 1}`,
                X: item.x || item.X || 0,
                Y: item.y || item.Y || 0,
                Radius: item.r || item.Radius || 15
            }));
        }
        return [];
    }

    _parseMultiSeriesData(data) {
        // Multi-series format: labels + dynamic series columns
        if (data && data.labels && data.datasets) {
            const rows = [];
            const numRows = data.labels.length;

            for (let i = 0; i < numRows; i++) {
                const row = {
                    id: `row-${i}`,
                    Label: data.labels[i]
                };

                // Add series data
                data.datasets.forEach((dataset, idx) => {
                    const seriesName = dataset.label || `Series ${idx + 1}`;
                    row[seriesName] = dataset.data[i] || 0;
                });

                rows.push(row);
            }

            return rows;
        }
        return [];
    }

    _parseSankeyData(data) {
        // Source, Target, Value format
        // Parse "Source → Target" arrow notation
        if (Array.isArray(data)) {
            return data.map((item, idx) => {
                const label = item.label || item.Label || '';
                const parts = label.split(/\s*→\s*|\s*->\s*/);

                return {
                    id: `row-${idx}`,
                    Source: parts[0] || '',
                    Target: parts[1] || '',
                    Value: item.value || item.Value || 0
                };
            });
        }
        return [];
    }

    _parseChoroplethData(data) {
        // State, Value format
        if (Array.isArray(data)) {
            return data.map((item, idx) => ({
                id: `row-${idx}`,
                State: item.label || item.Label || item.state || item.State || '',
                Value: item.value || item.Value || 0
            }));
        }
        return [];
    }

    /**
     * Convert column index to Excel-style letter (0→A, 1→B, 25→Z, 26→AA)
     */
    _getColumnLetter(index) {
        let letter = '';
        let num = index + 1;
        while (num > 0) {
            const mod = (num - 1) % 26;
            letter = String.fromCharCode(65 + mod) + letter;
            num = Math.floor((num - 1) / 26);
        }
        return letter;
    }

    /**
     * Get column configuration for chart type
     */
    _getColumnConfig() {
        const configs = {
            // Simple label-value charts
            'line': {
                columns: ['Label', 'Value'],
                activeColumns: ['Label', 'Value'],
                canAddColumns: false,
                columnTypes: { Label: 'text', Value: 'number' }
            },
            'bar_vertical': {
                columns: ['Label', 'Value'],
                activeColumns: ['Label', 'Value'],
                canAddColumns: false,
                columnTypes: { Label: 'text', Value: 'number' }
            },
            'bar_horizontal': {
                columns: ['Label', 'Value'],
                activeColumns: ['Label', 'Value'],
                canAddColumns: false,
                columnTypes: { Label: 'text', Value: 'number' }
            },
            'pie': {
                columns: ['Label', 'Value'],
                activeColumns: ['Label', 'Value'],
                canAddColumns: false,
                columnTypes: { Label: 'text', Value: 'number' }
            },
            'doughnut': {
                columns: ['Label', 'Value'],
                activeColumns: ['Label', 'Value'],
                canAddColumns: false,
                columnTypes: { Label: 'text', Value: 'number' }
            },
            'radar': {
                columns: ['Label', 'Value'],
                activeColumns: ['Label', 'Value'],
                canAddColumns: false,
                columnTypes: { Label: 'text', Value: 'number' }
            },
            'polar_area': {
                columns: ['Label', 'Value'],
                activeColumns: ['Label', 'Value'],
                canAddColumns: false,
                columnTypes: { Label: 'text', Value: 'number' }
            },
            'area': {
                columns: ['Label', 'Value'],
                activeColumns: ['Label', 'Value'],
                canAddColumns: false,
                columnTypes: { Label: 'text', Value: 'number' }
            },
            'waterfall': {
                columns: ['Label', 'Value'],
                activeColumns: ['Label', 'Value'],
                canAddColumns: false,
                columnTypes: { Label: 'text', Value: 'number' }
            },

            // Scatter chart
            'scatter': {
                columns: ['X', 'Y'],
                activeColumns: ['X', 'Y'],
                canAddColumns: false,
                columnTypes: { X: 'number', Y: 'number' }
            },

            // Bubble chart
            'bubble': {
                columns: ['Label', 'X', 'Y', 'Radius'],
                activeColumns: ['Label', 'X', 'Y', 'Radius'],
                canAddColumns: false,
                columnTypes: { Label: 'text', X: 'number', Y: 'number', Radius: 'number' }
            },

            // Multi-series charts (dynamic columns)
            'bar_grouped': this._getMultiSeriesConfig(),
            'bar_stacked': this._getMultiSeriesConfig(),
            'area_stacked': this._getMultiSeriesConfig(),

            // D3 charts
            'd3_treemap': {
                columns: ['Label', 'Value'],
                activeColumns: ['Label', 'Value'],
                canAddColumns: false,
                columnTypes: { Label: 'text', Value: 'number' },
                helpText: 'Use parent.child notation for hierarchies (e.g., "Revenue.Sales")'
            },
            'd3_sunburst': {
                columns: ['Label', 'Value'],
                activeColumns: ['Label', 'Value'],
                canAddColumns: false,
                columnTypes: { Label: 'text', Value: 'number' },
                helpText: 'Use parent.child notation for hierarchies (e.g., "Revenue.Sales")'
            },
            'd3_choropleth_usa': {
                columns: ['State', 'Value'],
                activeColumns: ['State', 'Value'],
                canAddColumns: false,
                columnTypes: { State: 'text', Value: 'number' },
                helpText: 'State names must be valid US states'
            },
            'd3_sankey': {
                columns: ['Source', 'Target', 'Value'],
                activeColumns: ['Source', 'Target', 'Value'],
                canAddColumns: false,
                columnTypes: { Source: 'text', Target: 'text', Value: 'number' },
                helpText: 'Each row represents a flow from Source to Target'
            }
        };

        // Auto-detect multi-series data based on parsed data structure
        // If chartType lookup fails but data has multi-series structure, return multi-series config
        let config = configs[this.chartType];

        if (!config && this.data && this.data.length > 0) {
            const firstRow = this.data[0];
            const rowKeys = Object.keys(firstRow).filter(k => k !== 'id');

            // If row has more than 2 columns (Label + multiple series columns), it's multi-series
            if (rowKeys.length > 2 || (rowKeys.length === 2 && !rowKeys.includes('Value'))) {
                console.log('🔍 Auto-detected multi-series structure in data');
                config = this._getMultiSeriesConfig();
            }
        }

        return config || configs['line'];
    }

    _getMultiSeriesConfig() {
        // Dynamically determine series columns from data
        const seriesColumns = [];
        if (this.data && this.data.length > 0) {
            const firstRow = this.data[0];
            Object.keys(firstRow).forEach(key => {
                if (key !== 'id' && key !== 'Label') {
                    seriesColumns.push(key);
                }
            });
        }

        const columns = ['Label', ...seriesColumns];
        const columnTypes = { Label: 'text' };
        seriesColumns.forEach(col => {
            columnTypes[col] = 'number';
        });

        return {
            columns: columns,
            activeColumns: [...columns],  // Create array copy to avoid duplicate additions
            canAddColumns: true,
            columnTypes: columnTypes
        };
    }

    /**
     * Render the Excel-like table
     */
    render(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        const html = `
            <div class="spreadsheet-editor-modal">
                <div class="spreadsheet-editor-overlay"></div>
                <div class="spreadsheet-editor-dialog">
                    <div class="spreadsheet-editor-header">
                        <h3>Edit Chart Data</h3>
                        <div class="spreadsheet-header-actions">
                            <button class="spreadsheet-help-btn" onclick="window.chartEditor_${this.safeChartId}.showHelp()" title="Show keyboard shortcuts and features">
                                ❓ Help
                            </button>
                            <button class="spreadsheet-close-btn" onclick="window.chartEditor_${this.safeChartId}.close()">&times;</button>
                        </div>
                    </div>

                    <!-- Help Modal (hidden by default) -->
                    <div id="spreadsheet-help-modal-${this.safeChartId}" class="spreadsheet-help-modal" style="display: none;">
                        <div class="spreadsheet-help-overlay" onclick="window.chartEditor_${this.safeChartId}.hideHelp()"></div>
                        <div class="spreadsheet-help-dialog">
                            <div class="spreadsheet-help-header">
                                <h3>📖 Excel-Style Editor Guide</h3>
                                <button class="spreadsheet-help-close" onclick="window.chartEditor_${this.safeChartId}.hideHelp()">&times;</button>
                            </div>
                            <div class="spreadsheet-help-content">
                                <div class="help-section">
                                    <h4>🖱️ Click Behavior</h4>
                                    <ul>
                                        <li><strong>Single click cell:</strong> Select (navigate, readonly mode)</li>
                                        <li><strong>Double click cell:</strong> Enter edit mode</li>
                                        <li><strong>Start typing:</strong> Auto-enter edit mode, replace value</li>
                                        <li><strong>Click column letter (A, B, C):</strong> Select entire column</li>
                                        <li><strong>Click row number (1, 2, 3):</strong> Select entire row</li>
                                    </ul>
                                </div>

                                <div class="help-section">
                                    <h4>⌨️ Keyboard Navigation</h4>
                                    <ul>
                                        <li><strong>Arrow keys:</strong> Navigate between cells</li>
                                        <li><strong>Tab:</strong> Move to next cell</li>
                                        <li><strong>Shift + Tab:</strong> Move to previous cell</li>
                                        <li><strong>Enter:</strong> Save and move down</li>
                                        <li><strong>Home:</strong> Jump to first cell in row</li>
                                        <li><strong>End:</strong> Jump to last cell in row</li>
                                        <li><strong>Ctrl/Cmd + Home:</strong> Jump to first cell (A1)</li>
                                        <li><strong>Ctrl/Cmd + End:</strong> Jump to last cell</li>
                                        <li><strong>Ctrl/Cmd + ↑:</strong> Jump to first row (same column)</li>
                                        <li><strong>Ctrl/Cmd + ↓:</strong> Jump to last row (same column)</li>
                                        <li><strong>Ctrl/Cmd + ←:</strong> Jump to first cell in row</li>
                                        <li><strong>Ctrl/Cmd + →:</strong> Jump to last cell in row</li>
                                    </ul>
                                </div>

                                <div class="help-section">
                                    <h4>✏️ Editing Features</h4>
                                    <ul>
                                        <li><strong>Add Row:</strong> Click "+ Add Row" button</li>
                                        <li><strong>Delete Row:</strong> Click 🗑️ icon in Actions column</li>
                                        <li><strong>Add Column:</strong> Click "+ Add Series" button (multi-series charts only)</li>
                                        <li><strong>Delete Column:</strong> Hover column header, click 🗑️ icon</li>
                                        <li><strong>Paste from Excel:</strong> Ctrl/Cmd + V (copies multiple cells)</li>
                                    </ul>
                                </div>

                                <div class="help-section">
                                    <h4>🎨 Visual Indicators</h4>
                                    <ul>
                                        <li><strong>Gray headers:</strong> Column letters and names</li>
                                        <li><strong>Blue border:</strong> Selected cell (readonly, navigate mode)</li>
                                        <li><strong>Green border:</strong> Editing cell (can type)</li>
                                        <li><strong>Light blue highlight:</strong> Selected column or row</li>
                                        <li><strong>Yellow background:</strong> Active data columns (with ✓)</li>
                                    </ul>
                                </div>

                                <div class="help-section help-section-tip">
                                    <h4>💡 Pro Tips</h4>
                                    <ul>
                                        <li>Use keyboard shortcuts for faster editing</li>
                                        <li>Double-click or start typing to edit</li>
                                        <li>Click column/row headers for quick selection</li>
                                        <li>Press Escape to cancel changes and close editor</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>

                    ${this.columnConfig.helpText ? `
                    <div class="spreadsheet-help-text">
                        <span class="help-icon">ℹ️</span> ${this.columnConfig.helpText}
                    </div>
                    ` : ''}

                    <div class="spreadsheet-editor-body">
                        <div class="spreadsheet-table-wrapper">
                            ${this._renderTable()}
                        </div>
                    </div>

                    <div class="spreadsheet-editor-footer">
                        <div class="spreadsheet-actions-left">
                            <button class="spreadsheet-btn spreadsheet-btn-secondary" onclick="window.chartEditor_${this.safeChartId}.addRow()">
                                + Add Row
                            </button>
                            ${this.columnConfig.canAddColumns ? `
                            <button class="spreadsheet-btn spreadsheet-btn-secondary" onclick="window.chartEditor_${this.safeChartId}.addSeriesColumn()">
                                + Add Series
                            </button>
                            ` : ''}
                        </div>
                        <div class="spreadsheet-actions-right">
                            <button class="spreadsheet-btn spreadsheet-btn-cancel" onclick="window.chartEditor_${this.safeChartId}.cancel()">
                                Cancel
                            </button>
                            <button class="spreadsheet-btn spreadsheet-btn-primary" onclick="window.chartEditor_${this.safeChartId}.save()">
                                Save & Update Chart
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            ${this._renderStyles()}
        `;

        container.innerHTML = html;
        this._attachTableEventListeners();
    }

    _renderTable() {
        const columns = this.columnConfig.columns;
        const activeColumns = this.columnConfig.activeColumns;

        let html = '<table class="spreadsheet-table" id="spreadsheet-table-' + this.chartId + '">';

        // Header - Excel-style dual rows
        html += '<thead>';

        // Row 1: Excel column letters (A, B, C, D...)
        html += '<tr class="excel-letter-row">';
        html += '<th class="spreadsheet-col-corner"></th>';  // Blank top-left corner

        columns.forEach((col, idx) => {
            const letter = this._getColumnLetter(idx);
            const isActive = activeColumns.includes(col);
            const activeClass = isActive ? 'spreadsheet-col-active' : '';
            html += `<th class="spreadsheet-col-letter ${activeClass}" data-column="${col}" data-col-index="${idx}">
                ${letter}
            </th>`;
        });

        html += '<th class="spreadsheet-col-actions-header"></th>';  // Blank for Actions column
        html += '</tr>';

        // Row 2: Column names (Label, North America, EMEA, etc.)
        html += '<tr class="excel-name-row">';
        html += '<th class="spreadsheet-row-header">#</th>';

        columns.forEach(col => {
            const isActive = activeColumns.includes(col);
            const activeClass = isActive ? 'spreadsheet-col-active' : '';
            const activeIcon = isActive ? '<span class="active-icon">✓</span>' : '';

            // Add delete button for series columns (not Label)
            const canDelete = this.columnConfig.canAddColumns && col !== 'Label';
            const deleteBtn = canDelete ?
                `<button class="spreadsheet-delete-col-btn"
                         onclick="window.chartEditor_${this.safeChartId}.deleteSeriesColumn('${col}')"
                         title="Delete series">🗑️</button>` : '';

            html += `<th class="spreadsheet-col-header ${activeClass}" data-column="${col}">
                <span class="col-header-content">
                    ${col} ${activeIcon}
                </span>
                ${deleteBtn}
            </th>`;
        });

        html += '<th class="spreadsheet-col-actions">Actions</th>';
        html += '</tr>';
        html += '</thead>';

        // Data rows
        html += '<tbody>';
        this.data.forEach((row, idx) => {
            html += this._renderRow(row, idx);
        });
        html += '</tbody>';

        html += '</table>';
        return html;
    }

    _renderRow(row, idx) {
        const columns = this.columnConfig.columns;
        const activeColumns = this.columnConfig.activeColumns;

        let html = `<tr data-row-id="${row.id}" data-row-index="${idx}">`;

        // Row number
        html += `<td class="spreadsheet-cell-number">${idx + 1}</td>`;

        // Data columns
        columns.forEach(col => {
            const value = row[col] !== undefined ? row[col] : '';
            const isActive = activeColumns.includes(col);
            const activeClass = isActive ? 'spreadsheet-cell-active' : '';
            const columnType = this.columnConfig.columnTypes[col] || 'text';
            // Always use type="text" to avoid browser spinner buttons
            const inputType = 'text';

            html += `<td class="spreadsheet-cell ${activeClass}"
                         data-row-id="${row.id}"
                         data-column="${col}"
                         data-column-type="${columnType}">
                <input type="${inputType}"
                       class="spreadsheet-input"
                       value="${value}"
                       data-row-id="${row.id}"
                       data-column="${col}"
                       readonly />
            </td>`;
        });

        // Actions column
        html += `<td class="spreadsheet-cell-actions">
            <button class="spreadsheet-delete-btn" onclick="window.chartEditor_${this.safeChartId}.deleteRow('${row.id}')" title="Delete row">
                🗑️
            </button>
        </td>`;

        html += '</tr>';
        return html;
    }

    _renderStyles() {
        return `
        <style>
            .spreadsheet-editor-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .spreadsheet-editor-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
            }

            .spreadsheet-editor-dialog {
                position: relative;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                width: 90%;
                max-width: 1200px;
                max-height: 90vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }

            .spreadsheet-editor-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 24px;
                border-bottom: 2px solid #e0e0e0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .spreadsheet-editor-header h3 {
                margin: 0;
                font-size: 20px;
                font-weight: 600;
            }

            .spreadsheet-header-actions {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .spreadsheet-help-btn {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .spreadsheet-help-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            }

            .spreadsheet-close-btn {
                background: transparent;
                border: none;
                color: white;
                font-size: 32px;
                cursor: pointer;
                padding: 0;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 4px;
                transition: background 0.2s;
            }

            .spreadsheet-close-btn:hover {
                background: rgba(255, 255, 255, 0.2);
            }

            .spreadsheet-help-text {
                padding: 12px 24px;
                background: #fff3cd;
                border-bottom: 1px solid #ffc107;
                color: #856404;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .help-icon {
                font-size: 16px;
            }

            .spreadsheet-editor-body {
                flex: 1;
                overflow: auto;
                padding: 20px 24px;
                background: #f8f9fa;
            }

            .spreadsheet-table-wrapper {
                background: white;
                border-radius: 4px;
                border: 1px solid #D4D4D4;
                overflow: auto;
                max-height: calc(90vh - 250px);
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }

            .spreadsheet-table {
                width: 100%;
                border-collapse: collapse;
                font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
                font-size: 11pt;
            }

            .spreadsheet-table th {
                background: #F2F2F2;
                color: #333333;
                font-weight: 400;
                padding: 8px;
                border: 1px solid #D4D4D4;
                position: sticky;
                top: 0;
                z-index: 10;
                text-align: center;
            }

            /* Excel-style dual-row header */
            .excel-letter-row th {
                background: #F2F2F2;
                border: 1px solid #D4D4D4;
                font-weight: 600;
                font-size: 11pt;
                color: #333333;
                text-align: center;
                padding: 6px 8px;
                position: sticky;
                top: 0;
                z-index: 12;
            }

            .excel-name-row th {
                background: #F2F2F2 !important;
                border: 1px solid #D4D4D4;
                font-weight: 400;
                font-size: 10pt;
                color: #333333;
                text-align: center;
                padding: 6px 8px;
                position: sticky;
                top: 32px;
                z-index: 11;
            }

            /* Ensure letter row also keeps gray background */
            .excel-letter-row th.spreadsheet-col-active {
                background: #F2F2F2 !important;
            }

            .spreadsheet-col-corner {
                background: #F2F2F2;
                border: 1px solid #D4D4D4;
                width: 50px;
            }

            .spreadsheet-col-letter {
                background: #F2F2F2;
                color: #333333;
                font-weight: 600;
                min-width: 80px;
                cursor: default;
            }

            .spreadsheet-row-header {
                background: #F2F2F2;
                color: #333333;
                font-weight: 400;
                width: 50px;
                text-align: center;
            }

            .spreadsheet-col-actions-header {
                background: #F2F2F2;
                border: 1px solid #D4D4D4;
                width: 80px;
            }

            .spreadsheet-col-active {
                background: #fff9db !important;
                position: relative;
            }

            .spreadsheet-col-active .active-icon {
                color: #28a745;
                font-weight: bold;
                margin-left: 4px;
            }

            .spreadsheet-col-number,
            .spreadsheet-cell-number {
                width: 50px;
                text-align: center;
                background: #F2F2F2;
                font-weight: 400;
                color: #333333;
                border: 1px solid #D4D4D4;
            }

            .spreadsheet-col-actions,
            .spreadsheet-cell-actions {
                width: 80px;
                text-align: center;
            }

            .spreadsheet-table td {
                padding: 0;
                border: 1px solid #D4D4D4;
                background: #FFFFFF;
            }

            .spreadsheet-cell {
                position: relative;
            }

            .spreadsheet-cell-active {
                background: #fffacd;
            }

            .spreadsheet-input {
                width: 100%;
                border: none;
                padding: 8px;
                font-size: 14px;
                font-family: inherit;
                background: transparent;
                outline: none;
                cursor: pointer;
            }

            /* Readonly state (selected, not editing) */
            .spreadsheet-input[readonly] {
                cursor: pointer;
                background: transparent;
            }

            .spreadsheet-input[readonly]:focus {
                background: #E7F3FF;
                box-shadow: inset 0 0 0 2px #4A90E2;
                outline: 2px solid #4A90E2;
                outline-offset: -2px;
            }

            /* Edit mode (not readonly) */
            .spreadsheet-input:not([readonly]):focus {
                background: #FFFFFF;
                box-shadow: inset 0 0 0 2px #217346;
                outline: 2px solid #217346;
                outline-offset: -2px;
                cursor: text;
            }

            .spreadsheet-table tr:hover td {
                background: #f8f9fa;
            }

            .spreadsheet-table tr:hover td.spreadsheet-cell-active {
                background: #fff3cd;
            }

            .spreadsheet-delete-btn {
                background: transparent;
                border: none;
                cursor: pointer;
                font-size: 18px;
                padding: 4px 8px;
                border-radius: 4px;
                transition: background 0.2s;
            }

            .spreadsheet-delete-btn:hover {
                background: #fee;
            }

            /* Column header layout and delete button */
            .spreadsheet-col-header {
                position: relative;
                padding: 12px 8px;
                text-align: center;
                vertical-align: middle;
            }

            .col-header-content {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 4px;
            }

            .spreadsheet-delete-col-btn {
                background: transparent;
                border: none;
                cursor: pointer;
                font-size: 14px;
                padding: 2px 6px;
                border-radius: 3px;
                transition: all 0.2s;
                opacity: 0;
                line-height: 1;
                flex-shrink: 0;
            }

            .spreadsheet-col-header:hover .spreadsheet-delete-col-btn {
                opacity: 1;
            }

            .spreadsheet-delete-col-btn:hover {
                background: #fee;
                transform: scale(1.1);
            }

            /* Excel-style column/row selection highlighting */
            .excel-selected-column {
                background: #E7F3FF !important;
                border-left: 1px solid #4A90E2;
                border-right: 1px solid #4A90E2;
            }

            .excel-selected-row {
                background: #E7F3FF !important;
                border-top: 1px solid #4A90E2;
                border-bottom: 1px solid #4A90E2;
            }

            .excel-selected-header {
                background: #4A90E2 !important;
                color: white !important;
            }

            .excel-selected-header .active-icon {
                color: white !important;
            }

            .spreadsheet-col-letter:hover,
            .spreadsheet-col-header:hover,
            .spreadsheet-cell-number:hover {
                background: #E8E8E8;
                cursor: pointer;
            }

            /* Help Modal Styles */
            .spreadsheet-help-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 15000;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .spreadsheet-help-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
            }

            .spreadsheet-help-dialog {
                position: relative;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                width: 90%;
                max-width: 700px;
                max-height: 80vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                z-index: 1;
            }

            .spreadsheet-help-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 24px;
                border-bottom: 2px solid #e0e0e0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .spreadsheet-help-header h3 {
                margin: 0;
                font-size: 20px;
                font-weight: 600;
            }

            .spreadsheet-help-close {
                background: transparent;
                border: none;
                color: white;
                font-size: 32px;
                cursor: pointer;
                padding: 0;
                width: 32px;
                height: 32px;
                line-height: 32px;
                transition: transform 0.2s;
            }

            .spreadsheet-help-close:hover {
                transform: scale(1.1);
            }

            .spreadsheet-help-content {
                padding: 24px;
                overflow-y: auto;
                flex: 1;
            }

            .help-section {
                margin-bottom: 24px;
            }

            .help-section:last-child {
                margin-bottom: 0;
            }

            .help-section h4 {
                margin: 0 0 12px 0;
                font-size: 16px;
                font-weight: 600;
                color: #333;
            }

            .help-section ul {
                margin: 0;
                padding-left: 20px;
                list-style-type: none;
            }

            .help-section li {
                margin-bottom: 8px;
                padding-left: 20px;
                position: relative;
                line-height: 1.5;
                color: #555;
            }

            .help-section li::before {
                content: "•";
                position: absolute;
                left: 0;
                color: #667eea;
                font-weight: bold;
                font-size: 18px;
            }

            .help-section strong {
                color: #333;
                font-weight: 600;
            }

            .help-section-tip {
                background: #f0f7ff;
                border-left: 4px solid #667eea;
                padding: 16px;
                border-radius: 6px;
            }

            .help-section-tip h4 {
                color: #667eea;
            }

            .spreadsheet-editor-footer {
                display: flex;
                justify-content: space-between;
                padding: 16px 24px;
                border-top: 2px solid #e0e0e0;
                background: #f8f9fa;
            }

            .spreadsheet-actions-left,
            .spreadsheet-actions-right {
                display: flex;
                gap: 12px;
            }

            .spreadsheet-btn {
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                border: none;
            }

            .spreadsheet-btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .spreadsheet-btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }

            .spreadsheet-btn-secondary {
                background: white;
                color: #667eea;
                border: 2px solid #667eea;
            }

            .spreadsheet-btn-secondary:hover {
                background: #f0f3ff;
            }

            .spreadsheet-btn-cancel {
                background: white;
                color: #6c757d;
                border: 2px solid #dee2e6;
            }

            .spreadsheet-btn-cancel:hover {
                background: #f8f9fa;
            }
        </style>
        `;
    }

    /**
     * Event listeners
     */
    _initializeEventListeners() {
        // Keyboard shortcuts (global)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'c') {
                    this._handleCopy(e);
                } else if (e.key === 'v') {
                    this._handlePaste(e);
                }
            }
        });
    }

    _attachTableEventListeners() {
        const table = document.getElementById(`spreadsheet-table-${this.chartId}`);
        if (!table) return;

        // Excel-style column header click (select entire column)
        table.addEventListener('click', (e) => {
            // Click on column letter
            if (e.target.classList.contains('spreadsheet-col-letter')) {
                const columnName = e.target.dataset.column;
                this._selectColumn(columnName);
                return;
            }

            // Click on column name header
            if (e.target.classList.contains('spreadsheet-col-header') ||
                e.target.closest('.spreadsheet-col-header')) {
                const header = e.target.classList.contains('spreadsheet-col-header') ?
                    e.target : e.target.closest('.spreadsheet-col-header');
                const columnName = header.dataset.column;
                if (columnName) {
                    this._selectColumn(columnName);
                    return;
                }
            }

            // Click on row number (select entire row)
            if (e.target.classList.contains('spreadsheet-cell-number')) {
                const row = e.target.closest('tr');
                const rowId = row.dataset.rowId;
                if (rowId) {
                    this._selectRow(rowId);
                    return;
                }
            }

            // Single click on cell input - select/focus (Excel-style)
            if (e.target.classList.contains('spreadsheet-input')) {
                this._clearSelection();
                e.target.focus();
                // Don't call select() - keep in readonly mode for navigation
                return;
            }
        });

        // Double-click on cell - enter edit mode (Excel-style)
        table.addEventListener('dblclick', (e) => {
            if (e.target.classList.contains('spreadsheet-input')) {
                e.target.removeAttribute('readonly');
                e.target.focus();
                // Position cursor at end
                const len = e.target.value.length;
                e.target.setSelectionRange(len, len);
            }
        });

        // Cell navigation
        table.addEventListener('keydown', (e) => {
            const input = e.target;
            if (!input.classList.contains('spreadsheet-input')) return;

            const cell = input.closest('td');
            const row = cell.closest('tr');

            // If readonly and user types a printable character, enter edit mode
            if (input.hasAttribute('readonly') && e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
                input.removeAttribute('readonly');
                input.value = '';  // Clear and start typing
                return;  // Let the character be typed
            }

            switch (e.key) {
                case 'Enter':
                    e.preventDefault();
                    this._navigateToNextRow(row, cell);
                    break;
                case 'Tab':
                    e.preventDefault();
                    if (e.shiftKey) {
                        this._navigateToPreviousCell(row, cell);
                    } else {
                        this._navigateToNextCell(row, cell);
                    }
                    break;
                case 'Home':
                    e.preventDefault();
                    if (e.ctrlKey) {
                        this._jumpToFirstCell();
                    } else {
                        this._jumpToFirstCellInRow(row);
                    }
                    break;
                case 'End':
                    e.preventDefault();
                    if (e.ctrlKey) {
                        this._jumpToLastCell();
                    } else {
                        this._jumpToLastCellInRow(row);
                    }
                    break;
                case 'ArrowUp':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this._jumpToFirstRow(cell);
                    } else if (input.hasAttribute('readonly')) {
                        // In readonly mode, always navigate
                        e.preventDefault();
                        this._navigateToPreviousRow(row, cell);
                    } else if (input.selectionStart === 0) {
                        // In edit mode, navigate only if cursor at start
                        e.preventDefault();
                        this._navigateToPreviousRow(row, cell);
                    }
                    break;
                case 'ArrowDown':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this._jumpToLastRow(cell);
                    } else if (input.hasAttribute('readonly')) {
                        // In readonly mode, always navigate
                        e.preventDefault();
                        this._navigateToNextRow(row, cell);
                    } else if (input.selectionStart === input.value.length) {
                        // In edit mode, navigate only if cursor at end
                        e.preventDefault();
                        this._navigateToNextRow(row, cell);
                    }
                    break;
                case 'ArrowLeft':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this._jumpToFirstCellInRow(row);
                    } else if (input.hasAttribute('readonly')) {
                        // In readonly mode, always navigate
                        e.preventDefault();
                        this._navigateToPreviousCell(row, cell);
                    } else if (input.selectionStart === 0) {
                        // In edit mode, navigate only if cursor at start
                        e.preventDefault();
                        this._navigateToPreviousCell(row, cell);
                    }
                    break;
                case 'ArrowRight':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this._jumpToLastCellInRow(row);
                    } else if (input.hasAttribute('readonly')) {
                        // In readonly mode, always navigate
                        e.preventDefault();
                        this._navigateToNextCell(row, cell);
                    } else if (input.selectionStart === input.value.length) {
                        // In edit mode, navigate only if cursor at end
                        e.preventDefault();
                        this._navigateToNextCell(row, cell);
                    }
                    break;
            }
        });

        // Auto-save on blur and restore readonly state
        table.addEventListener('blur', (e) => {
            if (e.target.classList.contains('spreadsheet-input')) {
                this._updateCellValue(e.target);
                // Restore readonly state (Excel-style: exit edit mode)
                e.target.setAttribute('readonly', 'readonly');
            }
        }, true);
    }

    _navigateToNextCell(row, currentCell) {
        const nextCell = currentCell.nextElementSibling;
        if (nextCell && nextCell.classList.contains('spreadsheet-cell')) {
            const input = nextCell.querySelector('.spreadsheet-input');
            if (input) {
                input.focus();
                input.select();
            }
        }
    }

    _navigateToPreviousCell(row, currentCell) {
        const prevCell = currentCell.previousElementSibling;
        if (prevCell && prevCell.classList.contains('spreadsheet-cell')) {
            const input = prevCell.querySelector('.spreadsheet-input');
            if (input) {
                input.focus();
                input.select();
            }
        } else if (prevCell && prevCell.classList.contains('spreadsheet-cell-number')) {
            // At start of row, go to previous row last cell
            const prevRow = row.previousElementSibling;
            if (prevRow) {
                const cells = prevRow.querySelectorAll('.spreadsheet-cell');
                const lastCell = cells[cells.length - 1];
                if (lastCell) {
                    const input = lastCell.querySelector('.spreadsheet-input');
                    if (input) {
                        input.focus();
                        input.select();
                    }
                }
            }
        }
    }

    _navigateToNextRow(row, currentCell) {
        const columnIndex = Array.from(row.children).indexOf(currentCell);
        const nextRow = row.nextElementSibling;
        if (nextRow) {
            const targetCell = nextRow.children[columnIndex];
            if (targetCell && targetCell.classList.contains('spreadsheet-cell')) {
                const input = targetCell.querySelector('.spreadsheet-input');
                if (input) {
                    input.focus();
                    input.select();
                }
            }
        }
    }

    _navigateToPreviousRow(row, currentCell) {
        const columnIndex = Array.from(row.children).indexOf(currentCell);
        const prevRow = row.previousElementSibling;
        if (prevRow) {
            const targetCell = prevRow.children[columnIndex];
            if (targetCell && targetCell.classList.contains('spreadsheet-cell')) {
                const input = targetCell.querySelector('.spreadsheet-input');
                if (input) {
                    input.focus();
                    input.select();
                }
            }
        }
    }

    /**
     * Excel-style jump navigation (Ctrl+Arrow, Home/End)
     */
    _jumpToFirstCell() {
        const table = document.getElementById(`spreadsheet-table-${this.chartId}`);
        const firstRow = table.querySelector('tbody tr:first-child');
        if (firstRow) {
            const firstCell = firstRow.querySelector('.spreadsheet-cell');
            if (firstCell) {
                const input = firstCell.querySelector('.spreadsheet-input');
                if (input) {
                    input.focus();
                    input.select();
                }
            }
        }
    }

    _jumpToLastCell() {
        const table = document.getElementById(`spreadsheet-table-${this.chartId}`);
        const lastRow = table.querySelector('tbody tr:last-child');
        if (lastRow) {
            const cells = lastRow.querySelectorAll('.spreadsheet-cell');
            const lastCell = cells[cells.length - 1];
            if (lastCell) {
                const input = lastCell.querySelector('.spreadsheet-input');
                if (input) {
                    input.focus();
                    input.select();
                }
            }
        }
    }

    _jumpToFirstCellInRow(row) {
        const firstCell = row.querySelector('.spreadsheet-cell');
        if (firstCell) {
            const input = firstCell.querySelector('.spreadsheet-input');
            if (input) {
                input.focus();
                input.select();
            }
        }
    }

    _jumpToLastCellInRow(row) {
        const cells = row.querySelectorAll('.spreadsheet-cell');
        const lastCell = cells[cells.length - 1];
        if (lastCell) {
            const input = lastCell.querySelector('.spreadsheet-input');
            if (input) {
                input.focus();
                input.select();
            }
        }
    }

    _jumpToFirstRow(currentCell) {
        const columnIndex = Array.from(currentCell.parentElement.children).indexOf(currentCell);
        const table = document.getElementById(`spreadsheet-table-${this.chartId}`);
        const firstRow = table.querySelector('tbody tr:first-child');
        if (firstRow) {
            const targetCell = firstRow.children[columnIndex];
            if (targetCell && targetCell.classList.contains('spreadsheet-cell')) {
                const input = targetCell.querySelector('.spreadsheet-input');
                if (input) {
                    input.focus();
                    input.select();
                }
            }
        }
    }

    _jumpToLastRow(currentCell) {
        const columnIndex = Array.from(currentCell.parentElement.children).indexOf(currentCell);
        const table = document.getElementById(`spreadsheet-table-${this.chartId}`);
        const lastRow = table.querySelector('tbody tr:last-child');
        if (lastRow) {
            const targetCell = lastRow.children[columnIndex];
            if (targetCell && targetCell.classList.contains('spreadsheet-cell')) {
                const input = targetCell.querySelector('.spreadsheet-input');
                if (input) {
                    input.focus();
                    input.select();
                }
            }
        }
    }

    _updateCellValue(input) {
        const rowId = input.dataset.rowId;
        const column = input.dataset.column;
        const value = input.value;

        // Find row in data
        const row = this.data.find(r => r.id === rowId);
        if (row) {
            // Validate and convert type
            const columnType = this.columnConfig.columnTypes[column];
            if (columnType === 'number') {
                const numValue = parseFloat(value);
                if (isNaN(numValue)) {
                    // Invalid number, revert
                    input.value = row[column];
                    this._showToast('Invalid number', 'error');
                    return;
                }
                row[column] = numValue;
            } else {
                row[column] = value;
            }
        }
    }

    /**
     * Copy/Paste handlers
     */
    _handleCopy(e) {
        const selection = window.getSelection();
        const selectedText = selection.toString();

        if (selectedText) {
            this.clipboard = selectedText;
        }
    }

    _handlePaste(e) {
        const input = document.activeElement;
        if (!input || !input.classList.contains('spreadsheet-input')) return;

        e.preventDefault();
        const pasteData = (e.clipboardData || window.clipboardData).getData('text');

        // Handle multi-row paste from Excel (tab/newline separated)
        const rows = pasteData.split(/\r?\n/).filter(row => row.trim());
        if (rows.length > 1) {
            this._pasteMultipleRows(input, rows);
        } else {
            // Single value paste
            input.value = pasteData;
            this._updateCellValue(input);
        }
    }

    _pasteMultipleRows(startInput, rows) {
        const startCell = startInput.closest('td');
        const startRow = startCell.closest('tr');
        const startColumnIndex = Array.from(startRow.children).indexOf(startCell);

        let currentRow = startRow;
        let rowIndex = 0;

        rows.forEach(rowData => {
            const cells = rowData.split('\t');
            let currentCell = currentRow.children[startColumnIndex];
            let cellIndex = 0;

            cells.forEach(cellValue => {
                if (currentCell && currentCell.classList.contains('spreadsheet-cell')) {
                    const input = currentCell.querySelector('.spreadsheet-input');
                    if (input) {
                        input.value = cellValue.trim();
                        this._updateCellValue(input);
                    }
                    currentCell = currentCell.nextElementSibling;
                }
                cellIndex++;
            });

            currentRow = currentRow.nextElementSibling;
            rowIndex++;

            // If we run out of rows, add new rows
            if (!currentRow && rowIndex < rows.length) {
                this.addRow();
                const table = document.getElementById(`spreadsheet-table-${this.chartId}`);
                const tbody = table.querySelector('tbody');
                currentRow = tbody.lastElementChild;
            }
        });

        this._showToast(`Pasted ${rows.length} rows`, 'success');
    }

    /**
     * Row operations
     */
    addRow() {
        const newRow = { id: `row-${Date.now()}` };

        // Initialize columns with default values
        this.columnConfig.columns.forEach(col => {
            const columnType = this.columnConfig.columnTypes[col];
            newRow[col] = columnType === 'number' ? 0 : '';
        });

        this.data.push(newRow);

        // Re-render table
        this._refreshTable();
        this._showToast('Row added', 'success');
    }

    deleteRow(rowId) {
        if (this.data.length <= 2) {
            this._showToast('Minimum 2 rows required', 'error');
            return;
        }

        this.data = this.data.filter(row => row.id !== rowId);
        this._refreshTable();
        this._showToast('Row deleted', 'success');
    }

    /**
     * Column operations (for multi-series charts)
     */
    addSeriesColumn() {
        if (!this.columnConfig.canAddColumns) return;

        const newSeriesName = prompt('Enter series name:', `Series ${this.columnConfig.columns.length}`);
        if (!newSeriesName) return;

        // Add column to config
        this.columnConfig.columns.push(newSeriesName);
        this.columnConfig.activeColumns.push(newSeriesName);
        this.columnConfig.columnTypes[newSeriesName] = 'number';

        // Add column to all rows
        this.data.forEach(row => {
            row[newSeriesName] = 0;
        });

        this._refreshTable();
        this._showToast(`Series "${newSeriesName}" added`, 'success');
    }

    deleteSeriesColumn(columnName) {
        if (!this.columnConfig.canAddColumns) return;

        // Prevent deletion of Label column
        if (columnName === 'Label') {
            this._showToast('Cannot delete Label column', 'error');
            return;
        }

        // Ensure at least 1 data column remains
        const dataColumns = this.columnConfig.columns.filter(col => col !== 'Label');
        if (dataColumns.length <= 1) {
            this._showToast('At least 1 data column required', 'error');
            return;
        }

        // Confirmation dialog
        if (!confirm(`Delete series "${columnName}"?\n\nThis will remove all data for this series.`)) {
            return;
        }

        // Remove from columnConfig
        this.columnConfig.columns = this.columnConfig.columns.filter(col => col !== columnName);
        this.columnConfig.activeColumns = this.columnConfig.activeColumns.filter(col => col !== columnName);
        delete this.columnConfig.columnTypes[columnName];

        // Remove from all data rows
        this.data.forEach(row => {
            delete row[columnName];
        });

        this._refreshTable();
        this._showToast(`Series "${columnName}" deleted`, 'success');
    }

    /**
     * Excel-style column/row selection
     */
    _selectColumn(columnName) {
        // Clear previous selection
        this._clearSelection();

        this.selectedColumn = columnName;

        // Highlight all cells in the column
        const table = document.getElementById(`spreadsheet-table-${this.chartId}`);
        const cells = table.querySelectorAll(`[data-column="${columnName}"]`);
        cells.forEach(cell => {
            if (cell.tagName === 'TH') {
                cell.classList.add('excel-selected-header');
            } else if (cell.tagName === 'TD') {
                cell.classList.add('excel-selected-column');
            }
        });

        console.log(`✓ Selected column: ${columnName}`);
    }

    _selectRow(rowId) {
        // Clear previous selection
        this._clearSelection();

        this.selectedRow = rowId;

        // Highlight all cells in the row
        const table = document.getElementById(`spreadsheet-table-${this.chartId}`);
        const row = table.querySelector(`tr[data-row-id="${rowId}"]`);
        if (row) {
            row.querySelectorAll('.spreadsheet-cell').forEach(cell => {
                cell.classList.add('excel-selected-row');
            });
            // Highlight row number
            const rowNum = row.querySelector('.spreadsheet-cell-number');
            if (rowNum) rowNum.classList.add('excel-selected-header');
        }

        console.log(`✓ Selected row: ${rowId}`);
    }

    _clearSelection() {
        this.selectedColumn = null;
        this.selectedRow = null;

        const table = document.getElementById(`spreadsheet-table-${this.chartId}`);
        if (table) {
            table.querySelectorAll('.excel-selected-column, .excel-selected-row, .excel-selected-header')
                .forEach(el => {
                    el.classList.remove('excel-selected-column', 'excel-selected-row', 'excel-selected-header');
                });
        }
    }

    /**
     * Save/Cancel operations
     */
    async save() {
        // Validate data
        const validation = this._validateData();
        if (!validation.valid) {
            this._showToast(validation.error, 'error');
            return;
        }

        // Convert internal data to chart format
        const chartData = this._exportData();

        // Call save handler
        try {
            await this.options.onSave(chartData, this.chartId);
            this._showToast('Chart updated successfully', 'success');

            // Close editor after brief delay
            setTimeout(() => this.close(), 1000);
        } catch (error) {
            this._showToast('Failed to save: ' + error.message, 'error');
        }
    }

    cancel() {
        // Revert to original data
        this.data = JSON.parse(JSON.stringify(this.originalData));
        this.close();
    }

    close() {
        const modal = document.querySelector('.spreadsheet-editor-modal');
        if (modal) {
            modal.remove();
        }
    }

    /**
     * Data validation
     */
    _validateData() {
        // Check minimum rows
        if (this.data.length < 2) {
            return { valid: false, error: 'Minimum 2 rows required' };
        }

        // Check maximum rows
        if (this.data.length > 50) {
            return { valid: false, error: 'Maximum 50 rows allowed' };
        }

        // Validate required columns
        for (const row of this.data) {
            for (const col of this.columnConfig.columns) {
                const value = row[col];
                const columnType = this.columnConfig.columnTypes[col];

                // Check empty values
                if (value === '' || value === null || value === undefined) {
                    return { valid: false, error: `Empty value in column "${col}"` };
                }

                // Check numeric types
                if (columnType === 'number') {
                    const num = parseFloat(value);
                    if (isNaN(num) || !isFinite(num)) {
                        return { valid: false, error: `Invalid number in column "${col}": ${value}` };
                    }
                }
            }
        }

        return { valid: true };
    }

    /**
     * Export data to chart format
     */
    _exportData() {
        const chartType = this.chartType;

        // Auto-detect multi-series format based on column structure
        const hasMultipleSeries = this.columnConfig.columns.length > 2;  // More than Label + 1 value column
        const hasValueColumn = this.columnConfig.columns.includes('Value');

        if (chartType === 'scatter') {
            return this.data.map(row => ({ x: row.X, y: row.Y }));
        } else if (chartType === 'bubble') {
            return this.data.map(row => ({ label: row.Label, x: row.X, y: row.Y, r: row.Radius }));
        } else if (['bar_grouped', 'bar_stacked', 'area_stacked'].includes(chartType) ||
                   (hasMultipleSeries && !hasValueColumn)) {
            // Multi-series format (explicit chartType OR auto-detected structure)
            const labels = this.data.map(row => row.Label);
            const seriesColumns = this.columnConfig.columns.filter(col => col !== 'Label');
            const datasets = seriesColumns.map(seriesName => ({
                label: seriesName,
                data: this.data.map(row => parseFloat(row[seriesName]) || 0)
            }));
            return { labels, datasets };
        } else if (chartType === 'd3_sankey') {
            // Reconstitute arrow notation
            return this.data.map(row => ({
                label: `${row.Source} → ${row.Target}`,
                value: row.Value
            }));
        } else if (chartType === 'd3_choropleth_usa') {
            return this.data.map(row => ({ label: row.State, value: row.Value }));
        } else {
            // Simple label-value format
            return this.data.map(row => ({ label: row.Label, value: row.Value }));
        }
    }

    /**
     * Refresh table display
     */
    _refreshTable() {
        const tableWrapper = document.querySelector('.spreadsheet-table-wrapper');
        if (tableWrapper) {
            tableWrapper.innerHTML = this._renderTable();
            this._attachTableEventListeners();
        }
    }

    /**
     * Help modal
     */
    showHelp() {
        const helpModal = document.getElementById(`spreadsheet-help-modal-${this.safeChartId}`);
        if (helpModal) {
            helpModal.style.display = 'flex';
        }
    }

    hideHelp() {
        const helpModal = document.getElementById(`spreadsheet-help-modal-${this.safeChartId}`);
        if (helpModal) {
            helpModal.style.display = 'none';
        }
    }

    /**
     * Toast notifications
     */
    _showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `spreadsheet-toast spreadsheet-toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            padding: 12px 20px;
            background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#17a2b8'};
            color: white;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 20000;
            font-size: 14px;
            font-weight: 500;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Default save handler
     */
    async _defaultSaveHandler(chartData, chartId) {
        // Send to API
        const response = await fetch(this.options.apiEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chart_id: chartId,
                data: chartData,
                timestamp: Date.now()
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save chart data');
        }

        // Update chart instance
        if (window.chartInstances && window.chartInstances[chartId]) {
            const chart = window.chartInstances[chartId];
            // Update chart data
            if (Array.isArray(chartData)) {
                chart.data.labels = chartData.map(d => d.label);
                chart.data.datasets[0].data = chartData.map(d => d.value);
            } else if (chartData.labels && chartData.datasets) {
                chart.data.labels = chartData.labels;
                chart.data.datasets = chartData.datasets;
            }
            chart.update();
        }
    }

    /**
     * Default cancel handler
     */
    _defaultCancelHandler() {
        console.log('Editor cancelled');
    }
}

// Global function to open editor
window.openChartEditor = function(chartId, chartType, chartData, options = {}) {
    const editorContainerId = `editor-container-${chartId}`;

    // Create container if doesn't exist
    let container = document.getElementById(editorContainerId);
    if (!container) {
        container = document.createElement('div');
        container.id = editorContainerId;
        document.body.appendChild(container);
    }

    // Create editor instance
    const editor = new ChartSpreadsheetEditor(chartId, chartType, chartData, options);
    const safeChartId = chartId.replace(/-/g, '_').replace(/\./g, '_').replace(/ /g, '_');
    window[`chartEditor_${safeChartId}`] = editor; // Make globally accessible

    // Render editor
    editor.render(editorContainerId);

    return editor;
}

// Add animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
