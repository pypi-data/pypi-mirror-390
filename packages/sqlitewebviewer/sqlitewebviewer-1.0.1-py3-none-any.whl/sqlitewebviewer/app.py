from flask import Flask, request, jsonify, render_template_string, send_file
import os
import sqlite3
import csv
from io import StringIO, BytesIO

# Supported SQLite file extensions
DB_EXTENSIONS = ('.db', '.sqlite', '.sqlite3')

def create_app():
    app = Flask(__name__)
    # ...Paste all your route/function code here...
    def scan_databases(base='.'):
        db_files = []
        for root, _, files in os.walk(base):
            for file in files:
                if file.lower().endswith(DB_EXTENSIONS):
                    db_files.append(os.path.relpath(os.path.join(root, file), base))
        return db_files

    def get_conn(db_rel_path):
        db_path = os.path.abspath(db_rel_path)
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file {db_rel_path} not found.")
        return sqlite3.connect(db_path)

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SQLite Browser - Database Management Tool</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            /* CSS Variables for Light/Dark Theme */
            :root {
                --background: 0 0% 100%;
                --foreground: 220 13% 13%;
                --border: 220 13% 91%;
                --card: 220 5% 97%;
                --card-foreground: 220 13% 13%;
                --card-border: 220 9% 89%;
                --primary: 217 91% 60%;
                --primary-foreground: 0 0% 100%;
                --secondary: 220 10% 86%;
                --secondary-foreground: 220 13% 13%;
                --muted: 220 11% 89%;
                --muted-foreground: 220 9% 46%;
                --accent: 220 13% 85%;
                --destructive: 0 84% 60%;
                --destructive-foreground: 0 0% 100%;
                --input: 220 13% 75%;
                --ring: 217 91% 60%;
            }

            .dark {
                --background: 220 6% 9%;
                --foreground: 220 8% 92%;
                --border: 220 8% 20%;
                --card: 220 5% 12%;
                --card-foreground: 220 8% 92%;
                --card-border: 220 7% 18%;
                --primary: 217 91% 60%;
                --primary-foreground: 0 0% 100%;
                --secondary: 220 7% 24%;
                --secondary-foreground: 220 8% 92%;
                --muted: 220 8% 20%;
                --muted-foreground: 220 10% 65%;
                --accent: 220 8% 22%;
                --destructive: 0 84% 60%;
                --destructive-foreground: 0 0% 100%;
                --input: 220 10% 40%;
                --ring: 217 91% 60%;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: hsl(var(--background));
                color: hsl(var(--foreground));
                line-height: 1.5;
                min-height: 100vh;
            }

            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 1.5rem;
            }

            /* Header */
            header {
                border-bottom: 1px solid hsl(var(--border));
                background: hsl(var(--background) / 0.95);
                backdrop-filter: blur(8px);
                position: sticky;
                top: 0;
                z-index: 50;
            }

            .header-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 1rem 0;
            }

            h1 {
                font-size: 1.5rem;
                font-weight: 600;
            }

            /* Controls Section */
            .controls-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 1rem;
                margin: 1.5rem 0;
            }

            @media (min-width: 768px) {
                .controls-grid {
                    grid-template-columns: 1fr 1fr;
                }
            }

            .form-group {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }

            label {
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: hsl(var(--muted-foreground));
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            select, input, textarea {
                width: 100%;
                padding: 0.5rem 0.75rem;
                border: 1px solid hsl(var(--border));
                border-radius: 0.375rem;
                background: hsl(var(--background));
                color: hsl(var(--foreground));
                font-size: 0.875rem;
                font-family: inherit;
            }

            select:focus, input:focus, textarea:focus {
                outline: none;
                border-color: hsl(var(--ring));
                box-shadow: 0 0 0 2px hsl(var(--ring) / 0.2);
            }

            textarea {
                font-family: 'JetBrains Mono', monospace;
                resize: vertical;
                min-height: 120px;
            }

            /* Card */
            .card {
                background: hsl(var(--card));
                border: 1px solid hsl(var(--card-border));
                border-radius: 0.5rem;
                overflow: hidden;
            }

            .card-header {
                padding: 1rem;
                border-bottom: 1px solid hsl(var(--border));
                background: hsl(var(--muted) / 0.3);
            }

            .card-content {
                padding: 1rem;
            }

            /* Info Card */
            .info-card {
                background: hsl(var(--muted) / 0.3);
                border: 1px solid hsl(var(--card-border));
                border-radius: 0.5rem;
                padding: 0.75rem;
                margin: 1.5rem 0;
                display: flex;
                gap: 0.5rem;
            }

            .info-card-content {
                flex: 1;
            }

            .info-label {
                font-size: 0.75rem;
                font-weight: 500;
                color: hsl(var(--muted-foreground));
                margin-bottom: 0.25rem;
            }

            .info-text {
                font-size: 0.875rem;
                font-family: 'JetBrains Mono', monospace;
                color: hsl(var(--foreground));
            }

            /* Button */
            .btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                border-radius: 0.375rem;
                font-size: 0.875rem;
                font-weight: 500;
                cursor: pointer;
                border: 1px solid transparent;
                transition: all 0.15s;
                white-space: nowrap;
            }

            .btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            .btn-primary {
                background: hsl(var(--primary));
                color: hsl(var(--primary-foreground));
                border-color: hsl(var(--primary));
            }

            .btn-primary:hover:not(:disabled) {
                opacity: 0.9;
            }

            .btn-outline {
                background: transparent;
                border: 1px solid hsl(var(--border));
                color: hsl(var(--foreground));
            }

            .btn-outline:hover:not(:disabled) {
                background: hsl(var(--accent));
            }

            .btn-ghost {
                background: transparent;
                color: hsl(var(--foreground));
            }

            .btn-ghost:hover:not(:disabled) {
                background: hsl(var(--accent));
            }

            .btn-sm {
                padding: 0.375rem 0.75rem;
                font-size: 0.813rem;
            }

            .btn-icon {
                padding: 0.5rem;
                width: 2.25rem;
                height: 2.25rem;
            }

            .btn-destructive {
                background: hsl(var(--destructive));
                color: hsl(var(--destructive-foreground));
            }

            .btn-destructive:hover:not(:disabled) {
                opacity: 0.9;
            }

            /* Table */
            .table-container {
                overflow-x: auto;
            }

            table {
                width: 100%;
                border-collapse: collapse;
            }

            th, td {
                padding: 0.75rem 1rem;
                text-align: left;
                border-bottom: 1px solid hsl(var(--border));
            }

            th {
                background: hsl(var(--muted) / 0.3);
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: hsl(var(--muted-foreground));
                white-space: nowrap;
            }

            td {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.875rem;
            }

            td[contenteditable="true"] {
                cursor: text;
            }

            td[contenteditable="true"]:hover {
                background: hsl(var(--accent) / 0.5);
            }

            td[contenteditable="true"]:focus {
                outline: 2px solid hsl(var(--ring));
                outline-offset: -2px;
                background: hsl(var(--accent));
            }

            tbody tr:hover {
                background: hsl(var(--muted) / 0.2);
            }

            /* Action Bar */
            .action-bar {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                justify-content: space-between;
                gap: 0.5rem;
            }

            .action-buttons {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
            }

            /* Pagination */
            .pagination {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                padding: 1rem;
                border-top: 1px solid hsl(var(--border));
            }

            /* Modal */
            .modal-overlay {
                display: none;
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.5);
                z-index: 100;
                align-items: center;
                justify-content: center;
            }

            .modal-overlay.active {
                display: flex;
            }

            .modal-content {
                background: hsl(var(--card));
                border: 1px solid hsl(var(--card-border));
                border-radius: 0.5rem;
                max-width: 500px;
                width: 90%;
                padding: 1.5rem;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
            }

            .modal-header {
                margin-bottom: 1rem;
            }

            .modal-title {
                font-size: 1.125rem;
                font-weight: 600;
            }

            .modal-description {
                font-size: 0.875rem;
                color: hsl(var(--muted-foreground));
                margin-top: 0.5rem;
            }

            .modal-footer {
                display: flex;
                gap: 0.5rem;
                justify-content: flex-end;
                margin-top: 1.5rem;
            }

            /* Insert Form */
            .insert-form {
                margin: 1rem 0;
            }

            .form-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 1rem;
                margin-bottom: 1rem;
            }

            @media (min-width: 768px) {
                .form-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }

            @media (min-width: 1024px) {
                .form-grid {
                    grid-template-columns: repeat(3, 1fr);
                }
            }

            /* Alert */
            .alert {
                padding: 1rem;
                border-radius: 0.375rem;
                display: flex;
                align-items: start;
                gap: 0.75rem;
                margin: 1rem 0;
            }

            .alert-error {
                background: hsl(var(--destructive) / 0.1);
                border: 1px solid hsl(var(--destructive) / 0.3);
                color: hsl(var(--destructive));
            }

            .alert-success {
                background: hsl(var(--primary) / 0.1);
                border: 1px solid hsl(var(--primary) / 0.3);
                color: hsl(var(--primary));
            }

            .alert-title {
                font-weight: 600;
                margin-bottom: 0.25rem;
            }

            .alert-message {
                font-size: 0.875rem;
            }

            /* Icons (using Unicode symbols) */
            .icon {
                display: inline-block;
                width: 1rem;
                height: 1rem;
            }

            /* Separator */
            .separator {
                height: 1px;
                background: hsl(var(--border));
                margin: 2rem 0;
            }

            /* Utility Classes */
            .hidden {
                display: none !important;
            }

            .text-muted {
                color: hsl(var(--muted-foreground));
            }

            .text-sm {
                font-size: 0.875rem;
            }

            .text-xs {
                font-size: 0.75rem;
            }

            .font-mono {
                font-family: 'JetBrains Mono', monospace;
            }

            .mb-2 {
                margin-bottom: 0.5rem;
            }

            .mb-4 {
                margin-bottom: 1rem;
            }

            .mt-4 {
                margin-top: 1rem;
            }

            .p-8 {
                padding: 2rem;
            }

            .text-center {
                text-align: center;
            }

            .space-y-4 > * + * {
                margin-top: 1rem;
            }

            .space-y-6 > * + * {
                margin-top: 1.5rem;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <div class="header-content">
                    <h1>SQLite Browser</h1>
                    <button id="theme-toggle" class="btn btn-ghost btn-icon" title="Toggle theme">
                        <span id="theme-icon">🌙</span>
                    </button>
                </div>
            </div>
        </header>

        <main class="container space-y-6" style="padding-top: 1.5rem; padding-bottom: 1.5rem;">
            <!-- Database and Table Selectors -->
            <div class="controls-grid">
                <div class="form-group">
                    <label for="database-select">📊 Database</label>
                    <select id="database-select" data-testid="select-database">
                        <option value="">Loading...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="table-select">📋 Table</label>
                    <select id="table-select" data-testid="select-table" disabled>
                        <option value="">Select database first</option>
                    </select>
                </div>
            </div>

            <!-- Column Info -->
            <div id="column-info" class="info-card hidden">
                <div style="margin-top: 2px;">ℹ️</div>
                <div class="info-card-content">
                    <div class="info-label">Columns</div>
                    <div id="column-text" class="info-text"></div>
                </div>
            </div>

            <!-- Insert Row Form -->
            <div id="insert-form-container" class="hidden">
                <div class="card">
                    <div class="card-header">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="font-size: 0.875rem; font-weight: 600;">Insert New Row</h3>
                            <button class="btn btn-ghost btn-sm" onclick="cancelInsert()">✕</button>
                        </div>
                    </div>
                    <div class="card-content">
                        <form id="insert-form" class="insert-form">
                            <div id="insert-fields" class="form-grid"></div>
                            <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
                                <button type="button" class="btn btn-outline" onclick="cancelInsert()">Cancel</button>
                                <button type="submit" class="btn btn-primary">Insert Row</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Data Table -->
            <div id="table-container" class="card hidden">
                <div class="card-header">
                    <div class="action-bar">
                        <div class="action-buttons">
                            <button class="btn btn-outline btn-sm" onclick="showInsertForm()" data-testid="button-insert-row">
                                ➕ Insert Row
                            </button>
                            <button class="btn btn-outline btn-sm" onclick="exportCSV()" data-testid="button-export-csv">
                                ⬇️ Export CSV
                            </button>
                        </div>
                        <div id="page-info" class="text-sm text-muted"></div>
                    </div>
                </div>
                <div class="table-container">
                    <table id="data-table">
                        <thead id="table-head"></thead>
                        <tbody id="table-body"></tbody>
                    </table>
                </div>
                <div id="pagination" class="pagination hidden"></div>
            </div>

            <div class="separator"></div>

            <!-- Query Editor -->
            <div class="card">
                <div class="card-header">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="font-size: 0.875rem; font-weight: 600;">SQL Query Editor</h3>
                        <span class="text-xs text-muted">Press Ctrl+Enter to run</span>
                    </div>
                </div>
                <div class="card-content space-y-4">
                    <textarea id="query-editor" placeholder="Enter your SQL query here..." data-testid="textarea-query"></textarea>
                    <div style="display: flex; justify-content: flex-end;">
                        <button id="run-query-btn" class="btn btn-primary" onclick="runQuery()" data-testid="button-run-query">
                            ▶️ Run Query
                        </button>
                    </div>
                </div>
            </div>

            <!-- Query Results -->
            <div id="query-results"></div>
        </main>

        <!-- Delete Confirmation Modal -->
        <div id="delete-modal" class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">Confirm Delete</h3>
                    <p class="modal-description">Are you sure you want to delete this row? This action cannot be undone.</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="closeDeleteModal()">Cancel</button>
                    <button class="btn btn-destructive" onclick="confirmDelete()">Delete</button>
                </div>
            </div>
        </div>

        <script>
            // State management
            const State = {
                databases: [],
                tables: [],
                columns: [],
                rows: [],
                selectedDB: '',
                selectedTable: '',
                currentPage: 1,
                totalPages: 1,
                pkIndex: 0,
                deleteRowId: null,
                theme: localStorage.getItem('theme') || 'light'
            };

            // Initialize theme
            function initTheme() {
                document.documentElement.classList.toggle('dark', State.theme === 'dark');
                document.getElementById('theme-icon').textContent = State.theme === 'light' ? '🌙' : '☀️';
            }

            // Toggle theme
            document.getElementById('theme-toggle').addEventListener('click', () => {
                State.theme = State.theme === 'light' ? 'dark' : 'light';
                localStorage.setItem('theme', State.theme);
                initTheme();
            });

            // API calls
            async function fetchDatabases() {
                const res = await fetch('/databases');
                const data = await res.json();
                State.databases = data.databases;
                renderDatabases();
            }

            async function fetchTables(db) {
                const res = await fetch(`/tables?db=${encodeURIComponent(db)}`);
                const data = await res.json();
                if (data.error) {
                    console.error('Error loading tables:', data.error);
                    State.tables = [];
                } else {
                    State.tables = data.tables;
                }
                renderTables();
            }

            async function fetchColumns(db, table) {
                const res = await fetch(`/columns?db=${encodeURIComponent(db)}&table=${encodeURIComponent(table)}`);
                const data = await res.json();
                if (data.error) {
                    console.error('Error loading columns:', data.error);
                    State.columns = [];
                } else {
                    State.columns = data.columns;
                }
                renderColumnInfo();
            }

            async function fetchTableData(page = 1) {
                const res = await fetch(`/tabledata?db=${encodeURIComponent(State.selectedDB)}&table=${encodeURIComponent(State.selectedTable)}&page=${page}`);
                const data = await res.json();
                if (data.error) {
                    console.error('Error loading table data:', data.error);
                    return;
                }
                State.rows = data.rows;
                State.currentPage = data.page;
                State.totalPages = data.pages;
                State.pkIndex = data.pkindex;
                renderTableData(data.columns, data.rows);
                renderPagination();
            }

            async function editCell(pkVal, column, newValue) {
                const res = await fetch('/editrow', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        db: State.selectedDB,
                        table: State.selectedTable,
                        pkindex: State.pkIndex,
                        pkval: pkVal,
                        col: column,
                        val: newValue
                    })
                });
                const data = await res.json();
                if (data.error) {
                    alert('Error updating cell: ' + data.error);
                    await fetchTableData(State.currentPage);
                }
            }

            async function deleteRow(pkVal) {
                const res = await fetch('/deleterow', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        db: State.selectedDB,
                        table: State.selectedTable,
                        pkval: pkVal
                    })
                });
                const data = await res.json();
                if (data.error) {
                    alert('Error deleting row: ' + data.error);
                }
                await fetchTableData(State.currentPage);
            }

            async function insertRow(values) {
                const res = await fetch('/insertrow', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        db: State.selectedDB,
                        table: State.selectedTable,
                        vals: values
                    })
                });
                const data = await res.json();
                if (data.error) {
                    alert('Error inserting row: ' + data.error);
                } else {
                    cancelInsert();
                    await fetchTableData(State.currentPage);
                }
            }

            async function runQuery() {
                const query = document.getElementById('query-editor').value;
                if (!query.trim() || !State.selectedDB) return;

                const runBtn = document.getElementById('run-query-btn');
                runBtn.disabled = true;
                runBtn.textContent = 'Running...';

                const res = await fetch('/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        db: State.selectedDB,
                        query: query
                    })
                });
                const data = await res.json();

                runBtn.disabled = false;
                runBtn.textContent = '▶️ Run Query';

                renderQueryResults(data);
            }

            function exportCSV() {
                window.location = `/exportcsv?db=${encodeURIComponent(State.selectedDB)}&table=${encodeURIComponent(State.selectedTable)}`;
            }

            // Render functions
            function renderDatabases() {
                const select = document.getElementById('database-select');
                select.innerHTML = '<option value="">Select database</option>';
                State.databases.forEach(db => {
                    const option = document.createElement('option');
                    option.value = db;
                    option.textContent = db;
                    select.appendChild(option);
                });
            }

            function renderTables() {
                const select = document.getElementById('table-select');
                select.disabled = State.tables.length === 0;
                select.innerHTML = State.tables.length === 0 
                    ? '<option value="">No tables</option>'
                    : '<option value="">Select table</option>';
                State.tables.forEach(table => {
                    const option = document.createElement('option');
                    option.value = table;
                    option.textContent = table;
                    select.appendChild(option);
                });
            }

            function renderColumnInfo() {
                const infoDiv = document.getElementById('column-info');
                const textDiv = document.getElementById('column-text');
                
                if (State.columns.length === 0) {
                    infoDiv.classList.add('hidden');
                    return;
                }

                infoDiv.classList.remove('hidden');
                textDiv.innerHTML = State.columns.map(col => 
                    `<span>${col.name} <span style="color: hsl(var(--muted-foreground));">(${col.type || 'NONE'})</span></span>`
                ).join(', ');

                // Update query editor with default query
                if (State.selectedTable) {
                    document.getElementById('query-editor').value = `SELECT * FROM ${State.selectedTable};`;
                }
            }

            function renderTableData(columns, rows) {
                const tableContainer = document.getElementById('table-container');
                const thead = document.getElementById('table-head');
                const tbody = document.getElementById('table-body');
                const pageInfo = document.getElementById('page-info');

                if (columns.length === 0) {
                    tableContainer.classList.add('hidden');
                    return;
                }

                tableContainer.classList.remove('hidden');

                // Render header
                thead.innerHTML = '<tr>' + 
                    columns.map(col => `<th>${col}</th>`).join('') +
                    '<th>Actions</th></tr>';

                // Render rows
                if (rows.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="${columns.length + 1}" style="text-align: center; padding: 2rem; color: hsl(var(--muted-foreground));">No data available</td></tr>`;
                } else {
                    tbody.innerHTML = rows.map((row, rowIdx) => {
                        const pkVal = row[State.pkIndex];
                        return '<tr>' + 
                            row.map((cell, colIdx) => 
                                `<td contenteditable="true" 
                                    data-pk="${pkVal}" 
                                    data-col="${columns[colIdx]}" 
                                    data-original="${cell === null ? '' : cell}"
                                    onblur="handleCellEdit(this)">${cell === null ? '' : cell}</td>`
                            ).join('') +
                            `<td><button class="btn btn-ghost btn-sm" onclick="openDeleteModal(${pkVal})" title="Delete row">🗑️</button></td>` +
                        '</tr>';
                    }).join('');
                }

                // Update page info
                if (State.totalPages > 1) {
                    pageInfo.textContent = `Page ${State.currentPage} of ${State.totalPages}`;
                } else {
                    pageInfo.textContent = '';
                }
            }

            function renderPagination() {
                const pagination = document.getElementById('pagination');
                
                if (State.totalPages <= 1) {
                    pagination.classList.add('hidden');
                    return;
                }

                pagination.classList.remove('hidden');
                
                let html = `<button class="btn btn-outline btn-sm" onclick="changePage(${State.currentPage - 1})" 
                            ${State.currentPage === 1 ? 'disabled' : ''}>◀</button>`;
                
                const maxButtons = 5;
                for (let i = 1; i <= Math.min(State.totalPages, maxButtons); i++) {
                    const btnClass = i === State.currentPage ? 'btn-primary' : 'btn-outline';
                    html += `<button class="btn ${btnClass} btn-sm" onclick="changePage(${i})">${i}</button>`;
                }
                
                if (State.totalPages > maxButtons) {
                    html += '<span style="color: hsl(var(--muted-foreground));">...</span>';
                }
                
                html += `<button class="btn btn-outline btn-sm" onclick="changePage(${State.currentPage + 1})" 
                        ${State.currentPage === State.totalPages ? 'disabled' : ''}>▶</button>`;
                
                pagination.innerHTML = html;
            }

            function renderQueryResults(data) {
                const container = document.getElementById('query-results');
                
                if (data.error) {
                    container.innerHTML = `
                        <div class="alert alert-error">
                            <div>⚠️</div>
                            <div>
                                <div class="alert-title">Query Error</div>
                                <div class="alert-message font-mono">${data.error}</div>
                            </div>
                        </div>
                    `;
                } else if (data.message) {
                    container.innerHTML = `
                        <div class="alert alert-success">
                            <div>✓</div>
                            <div>
                                <div class="alert-title">Success</div>
                                <div class="alert-message">${data.message}</div>
                            </div>
                        </div>
                    `;
                } else if (data.columns && data.rows) {
                    const rowCount = data.rows.length;
                    container.innerHTML = `
                        <div class="card">
                            <div class="card-header">
                                <div class="text-xs text-muted">${rowCount} ${rowCount === 1 ? 'row' : 'rows'} returned</div>
                            </div>
                            <div class="table-container">
                                <table>
                                    <thead>
                                        <tr>${data.columns.map(col => `<th>${col}</th>`).join('')}</tr>
                                    </thead>
                                    <tbody>
                                        ${data.rows.length === 0 
                                            ? `<tr><td colspan="${data.columns.length}" style="text-align: center; padding: 2rem; color: hsl(var(--muted-foreground));">No results</td></tr>`
                                            : data.rows.map(row => 
                                                `<tr>${row.map(cell => 
                                                    `<td>${cell === null ? '<span style="color: hsl(var(--muted-foreground)); font-style: italic;">null</span>' : cell}</td>`
                                                ).join('')}</tr>`
                                            ).join('')
                                        }
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;
                }
            }

            // Event handlers
            function handleCellEdit(cell) {
                const pkVal = cell.dataset.pk;
                const column = cell.dataset.col;
                const newValue = cell.textContent;
                const originalValue = cell.dataset.original;
                
                if (newValue !== originalValue) {
                    editCell(pkVal, column, newValue);
                }
            }

            function changePage(page) {
                if (page < 1 || page > State.totalPages) return;
                fetchTableData(page);
            }

            function showInsertForm() {
                const container = document.getElementById('insert-form-container');
                const fields = document.getElementById('insert-fields');
                
                fields.innerHTML = State.columns.map(col => `
                    <div class="form-group">
                        <label for="insert-${col.name}">${col.name} <span class="text-xs">(${col.type})</span></label>
                        <input type="text" id="insert-${col.name}" placeholder="${col.name}">
                    </div>
                `).join('');
                
                container.classList.remove('hidden');
            }

            function cancelInsert() {
                document.getElementById('insert-form-container').classList.add('hidden');
            }

            function openDeleteModal(pkVal) {
                State.deleteRowId = pkVal;
                document.getElementById('delete-modal').classList.add('active');
            }

            function closeDeleteModal() {
                State.deleteRowId = null;
                document.getElementById('delete-modal').classList.remove('active');
            }

            function confirmDelete() {
                if (State.deleteRowId !== null) {
                    deleteRow(State.deleteRowId);
                    closeDeleteModal();
                }
            }

            // Event listeners
            document.getElementById('database-select').addEventListener('change', async (e) => {
                State.selectedDB = e.target.value;
                State.selectedTable = '';
                State.columns = [];
                State.rows = [];
                
                if (State.selectedDB) {
                    await fetchTables(State.selectedDB);
                }
                
                document.getElementById('table-select').value = '';
                document.getElementById('column-info').classList.add('hidden');
                document.getElementById('table-container').classList.add('hidden');
            });

            document.getElementById('table-select').addEventListener('change', async (e) => {
                State.selectedTable = e.target.value;
                
                if (State.selectedTable && State.selectedDB) {
                    await fetchColumns(State.selectedDB, State.selectedTable);
                    await fetchTableData(1);
                } else {
                    document.getElementById('column-info').classList.add('hidden');
                    document.getElementById('table-container').classList.add('hidden');
                }
            });

            document.getElementById('insert-form').addEventListener('submit', (e) => {
                e.preventDefault();
                const values = State.columns.map(col => 
                    document.getElementById(`insert-${col.name}`).value
                );
                insertRow(values);
            });

            document.getElementById('query-editor').addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    runQuery();
                }
            });

            // Initialize
            initTheme();
            fetchDatabases();
        </script>
    </body>
    </html>
    """
    # FLASK ROUTES
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)

    @app.route('/databases')
    def databases():
        dbs = scan_databases('.')
        return jsonify({'databases': dbs})

    @app.route('/tables')
    def tables():
        db = request.args.get('db')
        try:
            conn = get_conn(db)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return jsonify({'tables': tables})
        except Exception as e:
            return jsonify({'error': str(e)})

    @app.route('/columns')
    def columns():
        db = request.args.get('db')
        table = request.args.get('table')
        try:
            conn = get_conn(db)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info('{table}')")
            columns = [{'cid': row[0], 'name': row[1], 'type': row[2], 'notnull': row[3], 'dflt_value': row[4], 'pk': row[5]} for row in cursor.fetchall()]
            conn.close()
            return jsonify({'columns': columns})
        except Exception as e:
            return jsonify({'error': str(e)})

    @app.route('/tabledata')
    def tabledata():
        db = request.args.get('db')
        table = request.args.get('table')
        page = int(request.args.get('page', 1))
        PAGE_SIZE = 20
        try:
            conn = get_conn(db)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info('{table}')")
            columns_info = cursor.fetchall()
            columns = [row[1] for row in columns_info]
            cursor.execute(f"SELECT COUNT(*) FROM \"{table}\";")
            count = cursor.fetchone()[0]
            pages = max(1, (count + PAGE_SIZE - 1) // PAGE_SIZE)
            offset = (page-1)*PAGE_SIZE
            cursor.execute(f"SELECT * FROM \"{table}\" LIMIT {PAGE_SIZE} OFFSET {offset}")
            rows = cursor.fetchall()
            pkindex = next((i for i,col in enumerate(columns_info) if col[5]), 0)
            conn.close()
            return jsonify({'columns': columns, 'rows': rows, 'page': page, 'pages': pages, 'pkindex':pkindex})
        except Exception as e:
            return jsonify({'error': str(e)})

    @app.route('/editrow', methods=['POST'])
    def editrow():
        data = request.get_json()
        db, table, pkindex, pkval, col, val = data['db'], data['table'], int(data['pkindex']), data['pkval'], data['col'], data['val']
        try:
            conn = get_conn(db)
            cursor = conn.cursor()
            pkcol = cursor.execute(f"PRAGMA table_info('{table}')").fetchall()[pkindex][1]
            cursor.execute(f"UPDATE \"{table}\" SET \"{col}\"=? WHERE \"{pkcol}\"=?",(val,pkval))
            conn.commit()
            conn.close()
            return jsonify({'ok':True})
        except Exception as e:
            return jsonify({'error':str(e)})

    @app.route('/deleterow',methods=['POST'])
    def deleterow():
        data=request.get_json()
        db,table,pkval=data['db'],data['table'],data['pkval']
        try:
            conn=get_conn(db)
            cursor=conn.cursor()
            pkcol=cursor.execute(f"PRAGMA table_info('{table}')").fetchall()[0][1]
            cursor.execute(f"DELETE FROM \"{table}\" WHERE \"{pkcol}\"=?",(pkval,))
            conn.commit()
            conn.close()
            return jsonify({'ok':True})
        except Exception as e:
            return jsonify({'error':str(e)})

    @app.route('/insertrow',methods=['POST'])
    def insertrow():
        data=request.get_json()
        db,table,vals=data['db'],data['table'],data['vals']
        try:
            conn=get_conn(db)
            cursor=conn.cursor()
            cursor.execute(f"PRAGMA table_info('{table}')")
            cols = [row[1] for row in cursor.fetchall()]
            q_marks = ",".join(["?"]*len(cols))
            cursor.execute(f"INSERT INTO \"{table}\" VALUES({q_marks})",vals)
            conn.commit()
            conn.close()
            return jsonify({'ok':True})
        except Exception as e:
            return jsonify({'error':str(e)})

    @app.route('/exportcsv')
    def exportcsv():
        db=request.args['db']
        table=request.args['table']
        conn=get_conn(db)
        cursor=conn.cursor()
        cursor.execute(f"SELECT * FROM \"{table}\"")
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([desc[0] for desc in cursor.description])
        writer.writerows(cursor.fetchall())
        csv_data = output.getvalue().encode('utf-8')
        output.close()
        return send_file(
            BytesIO(csv_data),
            download_name=f"{table}.csv",
            as_attachment=True,
            mimetype='text/csv'
        )

    @app.route('/query', methods=['POST'])
    def query():
        data = request.get_json()
        db = data.get('db')
        query_text = data.get('query')
        try:
            conn = get_conn(db)
            cursor = conn.cursor()
            cursor.execute(query_text)
            if query_text.strip().lower().startswith('select'):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                conn.close()
                return jsonify({'columns': columns, 'rows': rows})
            else:
                conn.commit()
                affected = cursor.rowcount
                conn.close()
                return jsonify({'message': f'Query executed successfully, {affected} rows affected.'})
        except Exception as e:
            return jsonify({'error': str(e)})

    # Return the configured Flask app instance
    return app

def main():
    import argparse
    import os as _os

    parser = argparse.ArgumentParser(description="Run the SQLite Web Viewer server")
    parser.add_argument("--host", default=_os.environ.get("HOST", "0.0.0.0"), help="Host interface to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(_os.environ.get("PORT", "8080")), help="Port to bind (default: 8080)")
    parser.add_argument("--debug", action="store_true", default=_os.environ.get("DEBUG", "").lower() in ("1", "true", "yes"), help="Enable Flask debug mode")
    args = parser.parse_args()

    app = create_app()
    app.run(debug=args.debug, host=args.host, port=args.port)

if __name__ == '__main__':
    main()

