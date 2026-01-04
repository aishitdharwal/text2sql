// Dashboard page JavaScript
const API_BASE_URL = 'http://localhost:8080/api';

// State management
let sessionId = null;
let team = null;
let database = null;
let currentTables = [];
let currentSchemas = {};

// Initialize dashboard
function init() {
    // Check if user is logged in
    sessionId = sessionStorage.getItem('sessionId');
    team = sessionStorage.getItem('team');
    database = sessionStorage.getItem('database');
    
    if (!sessionId) {
        window.location.href = '/';
        return;
    }
    
    // Update UI with user info
    document.getElementById('teamName').textContent = `Team: ${team}`;
    document.getElementById('databaseName').textContent = `Database: ${database}`;
    
    // Load tables
    loadTables();
    
    // Setup event listeners
    setupEventListeners();
}

function setupEventListeners() {
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // Generate query
    document.getElementById('generateBtn').addEventListener('click', generateQuery);
    
    // Execute query
    document.getElementById('executeBtn').addEventListener('click', executeQuery);
    
    // Clear
    document.getElementById('clearBtn').addEventListener('click', clearQuery);
    
    // Enable execute button when SQL is manually entered
    document.getElementById('sqlQueryInput').addEventListener('input', (e) => {
        const executeBtn = document.getElementById('executeBtn');
        executeBtn.disabled = e.target.value.trim() === '';
    });
}

async function logout() {
    try {
        await fetch(`${API_BASE_URL}/logout?session_id=${sessionId}`, {
            method: 'POST'
        });
    } catch (error) {
        console.error('Logout error:', error);
    }
    
    sessionStorage.clear();
    window.location.href = '/';
}

async function loadTables() {
    const loadingDiv = document.getElementById('loadingTables');
    const tablesListDiv = document.getElementById('tablesList');
    
    try {
        const response = await fetch(`${API_BASE_URL}/tables?session_id=${sessionId}`);
        const data = await response.json();
        
        if (data.success) {
            currentTables = data.tables;
            loadingDiv.style.display = 'none';
            
            // Render tables list
            tablesListDiv.innerHTML = data.tables.map(table => `
                <div class="table-item" data-table="${table.table_name}">
                    <div class="table-name">${table.table_name}</div>
                    ${table.table_comment ? `<div class="table-description">${table.table_comment}</div>` : ''}
                </div>
            `).join('');
            
            // Add click handlers
            document.querySelectorAll('.table-item').forEach(item => {
                item.addEventListener('click', () => loadTableSchema(item.dataset.table));
            });
            
            // Load all schemas
            await loadAllSchemas();
        }
    } catch (error) {
        console.error('Error loading tables:', error);
        loadingDiv.textContent = 'Error loading tables';
    }
}

async function loadAllSchemas() {
    try {
        const response = await fetch(`${API_BASE_URL}/schema?session_id=${sessionId}`);
        const data = await response.json();
        
        if (data.success) {
            currentSchemas = data.schemas;
        }
    } catch (error) {
        console.error('Error loading schemas:', error);
    }
}

function loadTableSchema(tableName) {
    // Update active table
    document.querySelectorAll('.table-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-table="${tableName}"]`).classList.add('active');
    
    // Show schema
    const schemaDetailsDiv = document.getElementById('schemaDetails');
    const schema = currentSchemas[tableName];
    
    if (!schema) {
        schemaDetailsDiv.innerHTML = '<p class="info-text">Schema not found</p>';
        return;
    }
    
    let html = `<h3>${tableName}</h3>`;
    if (schema.comment) {
        html += `<p style="color: #666; margin-bottom: 15px; font-size: 13px;">${schema.comment}</p>`;
    }
    
    html += schema.columns.map(col => `
        <div class="column-item">
            <div class="column-name">
                ${col.column_name}
                ${col.is_nullable === 'NO' ? '<span class="not-null-badge">NOT NULL</span>' : ''}
            </div>
            <div class="column-type">${col.data_type}</div>
            ${col.column_comment ? `<div class="column-description">${col.column_comment}</div>` : ''}
        </div>
    `).join('');
    
    schemaDetailsDiv.innerHTML = html;
}

async function generateQuery() {
    const naturalLanguageInput = document.getElementById('naturalLanguageInput').value.trim();
    const sqlQueryInput = document.getElementById('sqlQueryInput');
    const generateBtn = document.getElementById('generateBtn');
    const executeBtn = document.getElementById('executeBtn');
    const loadingDiv = document.getElementById('loadingQuery');
    const errorDiv = document.getElementById('errorMessage');
    
    if (!naturalLanguageInput) {
        alert('Please enter a question');
        return;
    }
    
    // Show loading
    loadingDiv.style.display = 'block';
    generateBtn.disabled = true;
    sqlQueryInput.value = '';
    executeBtn.disabled = true;
    errorDiv.style.display = 'none';
    
    // Clear previous results
    clearResults();
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate-query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                natural_language_query: naturalLanguageInput
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            sqlQueryInput.value = data.sql_query;
            executeBtn.disabled = false;
        } else {
            errorDiv.textContent = `Error generating query: ${data.error}`;
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Error generating query:', error);
        errorDiv.textContent = 'Network error generating query';
        errorDiv.style.display = 'block';
    } finally {
        loadingDiv.style.display = 'none';
        generateBtn.disabled = false;
    }
}

async function executeQuery() {
    const sqlQueryInput = document.getElementById('sqlQueryInput').value.trim();
    const executeBtn = document.getElementById('executeBtn');
    const loadingDiv = document.getElementById('loadingResults');
    const errorDiv = document.getElementById('errorMessage');
    const resultsInfoDiv = document.getElementById('resultsInfo');
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (!sqlQueryInput) {
        alert('No SQL query to execute');
        return;
    }
    
    // Show loading
    loadingDiv.style.display = 'block';
    executeBtn.disabled = true;
    errorDiv.style.display = 'none';
    resultsInfoDiv.style.display = 'none';
    resultsContainer.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE_URL}/execute-query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                sql_query: sqlQueryInput
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.data) {
                // Show results table
                displayResults(data.data);
                resultsInfoDiv.textContent = `Query returned ${data.row_count} row(s)`;
                resultsInfoDiv.style.display = 'block';
            } else {
                resultsInfoDiv.textContent = data.message || `Query executed successfully. ${data.rows_affected} row(s) affected.`;
                resultsInfoDiv.style.display = 'block';
            }
        } else {
            errorDiv.textContent = `Query Error: ${data.error}`;
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Error executing query:', error);
        errorDiv.textContent = 'Network error executing query';
        errorDiv.style.display = 'block';
    } finally {
        loadingDiv.style.display = 'none';
        executeBtn.disabled = false;
    }
}

function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (!data || data.length === 0) {
        resultsContainer.innerHTML = '<p class="info-text">No results found</p>';
        return;
    }
    
    // Get column names from first row
    const columns = Object.keys(data[0]);
    
    // Build table
    let html = '<table class="results-table"><thead><tr>';
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const value = row[col];
            html += `<td>${value !== null ? value : '<i>NULL</i>'}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    resultsContainer.innerHTML = html;
}

function clearQuery() {
    document.getElementById('naturalLanguageInput').value = '';
    document.getElementById('sqlQueryInput').value = '';
    document.getElementById('executeBtn').disabled = true;
    clearResults();
}

function clearResults() {
    document.getElementById('errorMessage').style.display = 'none';
    document.getElementById('resultsInfo').style.display = 'none';
    document.getElementById('resultsContainer').innerHTML = '';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
