// Chat Interface JavaScript

// State management
let isProcessing = false;
let userId = 'user_' + Math.random().toString(36).substr(2, 9);

// DOM elements
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const chatForm = document.getElementById('chatForm');
const sendButton = document.getElementById('sendButton');
const statusIndicator = document.getElementById('statusIndicator');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEventListeners();
    autoResizeTextarea();
});

// Setup event listeners
function setupEventListeners() {
    chatForm.addEventListener('submit', handleSubmit);

    // Auto-resize textarea
    messageInput.addEventListener('input', autoResizeTextarea);

    // Handle Enter key
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
}

// Auto-resize textarea based on content
function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
}

// Check server health
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.status === 'healthy') {
            updateStatus('connected', 'Connected');
        } else {
            updateStatus('error', 'Connection Error');
        }
    } catch (error) {
        updateStatus('error', 'Server Offline');
    }
}

// Update status indicator
function updateStatus(status, text) {
    statusIndicator.className = `status-indicator ${status}`;
    statusIndicator.querySelector('.status-text').textContent = text;
}

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();

    if (isProcessing) return;

    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');

    // Clear input
    messageInput.value = '';
    autoResizeTextarea();

    // Show loading
    const loadingId = addLoadingMessage();

    // Disable input
    isProcessing = true;
    sendButton.disabled = true;

    try {
        // Send message to server
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                user_id: userId
            })
        });

        const data = await response.json();

        // Remove loading message
        removeMessage(loadingId);

        if (data.success) {
            // Add bot response
            addBotResponse(data);
        } else {
            // Show error
            addErrorMessage(data.message || data.error || 'Terjadi kesalahan');
        }
    } catch (error) {
        removeMessage(loadingId);
        addErrorMessage('Gagal terhubung ke server. Silakan coba lagi.');
        console.error('Error:', error);
    } finally {
        isProcessing = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
}

// Add message to chat
function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.id = `msg_${Date.now()}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;

    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    scrollToBottom();

    return messageDiv.id;
}

// Add loading/typing indicator
function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    const loadingId = `loading_${Date.now()}`;
    messageDiv.id = loadingId;
    messageDiv.className = 'message bot-message';

    // Use styling from style.css
    const contentDiv = document.createElement('div');
    contentDiv.innerHTML = `
        <div class="typing-indicator">
            <span style="font-size: 13px; color: var(--text-tertiary); margin-right: 8px;">Thinking</span>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;

    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    scrollToBottom();

    return loadingId;
}

// Add bot response with suggested queries
function addBotResponse(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Add explanation text
    if (data.message) {
        const textP = document.createElement('p');
        textP.textContent = data.message;
        contentDiv.appendChild(textP);
    }

    // Add suggested queries
    if (data.suggested_queries && data.suggested_queries.length > 0) {
        const queriesDiv = document.createElement('div');
        queriesDiv.className = 'suggested-queries';

        const title = document.createElement('h4');
        title.textContent = '💡 Suggested SQL Queries:';
        queriesDiv.appendChild(title);

        data.suggested_queries.forEach((query, index) => {
            const queryItem = document.createElement('div');
            queryItem.className = 'query-item';

            const sqlDiv = document.createElement('div');
            sqlDiv.className = 'query-sql';
            sqlDiv.textContent = query.sql;
            queryItem.appendChild(sqlDiv);

            const explanationDiv = document.createElement('div');
            explanationDiv.className = 'query-explanation';
            explanationDiv.textContent = query.explanation;
            queryItem.appendChild(explanationDiv);

            const executeBtn = document.createElement('button');
            executeBtn.className = 'execute-button';
            executeBtn.textContent = `▶ Execute Query #${index + 1}`;
            executeBtn.onclick = () => executeQuery(index);
            queryItem.appendChild(executeBtn);

            queriesDiv.appendChild(queryItem);
        });

        contentDiv.appendChild(queriesDiv);
    }

    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Execute a suggested query
async function executeQuery(queryIndex) {
    const loadingId = addLoadingMessage();

    try {
        const response = await fetch(`/api/execute/${queryIndex}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId
            })
        });

        const data = await response.json();

        removeMessage(loadingId);

        if (data.success) {
            // Add query index to data for CSV export
            data.query_index = queryIndex;
            addQueryResults(data);
        } else {
            addErrorMessage(data.message || data.error || 'Query execution failed');
        }
    } catch (error) {
        removeMessage(loadingId);
        addErrorMessage('Gagal menjalankan query. Silakan coba lagi.');
        console.error('Error:', error);
    }
}

// Add query results to chat
function addQueryResults(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Add SQL query
    const sqlDiv = document.createElement('div');
    sqlDiv.innerHTML = `<strong>📊 Query Executed:</strong>`;
    contentDiv.appendChild(sqlDiv);

    const resultsDiv = document.createElement('div');
    resultsDiv.className = 'results-table';
    const pre = document.createElement('pre');
    pre.textContent = data.sql_query;
    resultsDiv.appendChild(pre);
    contentDiv.appendChild(resultsDiv);

    // Add table results
    if (data.results && data.results.length > 0) {
        const tableDiv = document.createElement('div');
        tableDiv.innerHTML = `<strong>📋 Results (${data.row_count} rows):</strong>`;
        contentDiv.appendChild(tableDiv);

        const resultsContainer = document.createElement('div');
        resultsContainer.className = 'results-container';

        // 1. Create HTML Table
        const table = document.createElement('table');
        table.className = 'data-table';

        // Header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const columns = Object.keys(data.results[0]);
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Body
        const tbody = document.createElement('tbody');
        data.results.forEach(row => {
            const tr = document.createElement('tr');
            columns.forEach(col => {
                const td = document.createElement('td');
                td.textContent = row[col];
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        const tableWrapper = document.createElement('div');
        tableWrapper.className = 'table-wrapper';
        tableWrapper.appendChild(table);
        resultsContainer.appendChild(tableWrapper);

        // 2. Add Export Buttons
        const exportButtons = document.createElement('div');
        exportButtons.className = 'export-buttons';

        const csvBtn = document.createElement('button');
        csvBtn.className = 'export-button csv-button';
        csvBtn.innerHTML = '📥 Download CSV';
        csvBtn.onclick = () => downloadCSV(data.query_index || 0);
        exportButtons.appendChild(csvBtn);

        resultsContainer.appendChild(exportButtons);

        // 3. Generate Chart if visualization data available
        if (data.visualization && data.visualization.can_visualize) {
            const vizData = data.visualization;
            const chartWrapper = document.createElement('div');
            chartWrapper.className = 'chart-wrapper';

            // Chart header
            const chartHeader = document.createElement('div');
            chartHeader.className = 'chart-header';
            const chartTitle = document.createElement('h4');
            chartTitle.innerHTML = `📊 Visualization: ${vizData.chart_type.charAt(0).toUpperCase() + vizData.chart_type.slice(1)} Chart`;
            chartHeader.appendChild(chartTitle);

            const chartInfo = document.createElement('span');
            chartInfo.className = 'chart-info';
            chartInfo.textContent = vizData.reason || '';
            chartHeader.appendChild(chartInfo);

            chartWrapper.appendChild(chartHeader);

            // Canvas for chart
            const canvas = document.createElement('canvas');
            const chartId = `chart_${Date.now()}`;
            canvas.id = chartId;
            chartWrapper.appendChild(canvas);

            // Debug Info (Hidden by default)
            const debugDetails = document.createElement('details');
            debugDetails.style.marginTop = '10px';
            debugDetails.style.color = '#64748b';
            debugDetails.style.fontSize = '11px';
            const debugSummary = document.createElement('summary');
            debugSummary.textContent = '🛠️ Debug Visualization Data';
            debugSummary.style.cursor = 'pointer';
            debugDetails.appendChild(debugSummary);
            const debugPre = document.createElement('pre');
            debugPre.textContent = JSON.stringify(vizData, null, 2);
            debugPre.style.whiteSpace = 'pre-wrap';
            debugPre.style.marginTop = '5px';
            debugDetails.appendChild(debugPre);
            chartWrapper.appendChild(debugDetails);

            resultsContainer.appendChild(chartWrapper);

            // Render chart after DOM update
            setTimeout(() => {
                renderChart(canvas, vizData.chart_data);
            }, 100);
        } else if (data.visualization && !data.visualization.can_visualize) {
            // Show why visualization is not available
            const vizNote = document.createElement('div');
            vizNote.className = 'viz-note';
            vizNote.innerHTML = `<em>ℹ️ ${data.visualization.reason || 'Visualization not available for this data'}</em>`;
            resultsContainer.appendChild(vizNote);
        }

        contentDiv.appendChild(resultsContainer);
    }

    // Add natural language summary
    if (data.nl_summary) {
        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'nl-summary';
        summaryDiv.innerHTML = `<strong>💬 Summary:</strong><br>${escapeHtml(data.nl_summary)}`;
        contentDiv.appendChild(summaryDiv);
    }

    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    scrollToBottom();

    // Store query index for CSV export
    if (data.query_index === undefined) {
        // Try to infer from last execution
        const lastExecMatch = data.sql_query.match(/Query #(\d+)/);
        if (lastExecMatch) {
            data.query_index = parseInt(lastExecMatch[1]);
        }
    }
}

// Render chart using Chart.js
function renderChart(canvas, chartData) {
    try {
        const ctx = canvas.getContext('2d');

        // Create gradient
        let bgGradient = null;
        if (chartData.type === 'bar' || chartData.type === 'line' || chartData.type === 'scatter') {
            bgGradient = ctx.createLinearGradient(0, 0, 0, 400);
            bgGradient.addColorStop(0, 'rgba(99, 102, 241, 0.8)'); // Primary
            bgGradient.addColorStop(1, 'rgba(236, 72, 153, 0.2)'); // Secondary
        }

        // Apply gradient to datasets if suitable
        if (bgGradient && chartData.datasets.length === 1) {
            chartData.datasets[0].backgroundColor = bgGradient;
            chartData.datasets[0].borderColor = '#818cf8';
            chartData.datasets[0].borderWidth = 0;
            chartData.datasets[0].borderRadius = 6;
        }

        // Chart.js configuration
        const config = {
            type: chartData.type,
            data: {
                labels: chartData.labels,
                datasets: chartData.datasets
            },
            options: {
                is_dual_axis: chartData.is_dual_axis, // Custom prop for scales config
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: chartData.type === 'pie' ? 1.5 : 1.3,
                indexAxis: chartData.indexAxis || 'x',  // 'y' for horizontal bars
                devicePixelRatio: window.devicePixelRatio || 2,
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: {
                        position: chartData.type === 'pie' ? 'right' : 'top',
                        align: 'center',
                        labels: {
                            color: '#e2e8f0',
                            font: { family: 'Inter', size: 12 },
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8,
                        displayColors: true,
                        callbacks: chartData.type === 'pie' ? {
                            label: function (context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${Intl.NumberFormat('id-ID').format(value)} (${percentage}%)`;
                            }
                        } : {
                            label: function (context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';

                                // Handling Scatter Points
                                if (context.raw && context.raw.x !== undefined) {
                                    return `${label} (${context.raw.x}, ${context.raw.y})`;
                                }

                                if (context.parsed.y !== null) {
                                    label += Intl.NumberFormat('id-ID').format(context.parsed.y);
                                }
                                return label;
                            },
                            afterBody: function (context) {
                                // Support for "Mixed Scale" tooltips (extra_info)
                                const dataPoint = context[0];
                                const dataset = dataPoint.dataset;

                                if (dataset.extra_info && dataset.extra_info[dataPoint.dataIndex]) {
                                    const extras = dataset.extra_info[dataPoint.dataIndex];
                                    return Object.entries(extras).map(([k, v]) => `\n${k}: ${v}`);
                                }
                                return [];
                            }
                        }
                    }
                },
                scales: chartData.is_horizontal_combo ? {
                    y: {
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } },
                        title: { display: true, text: 'Categories', color: '#94a3b8' }
                    },
                    xRevenue: {
                        position: 'bottom',
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } },
                        grid: { color: 'rgba(148, 163, 184, 0.05)' },
                        title: {
                            display: true,
                            text: chartData.primaryAxisTitle,
                            color: '#94a3b8'
                        }
                    },
                    xRating: {
                        position: 'top',
                        min: 0,
                        max: 5,
                        ticks: { stepSize: 1, color: '#10b981' },
                        grid: { display: false },
                        title: {
                            display: true,
                            text: chartData.secondaryAxisTitle + ' (0-5)',
                            color: '#10b981'
                        }
                    }
                } : (chartData.type !== 'pie' ? {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } },
                        grid: { color: 'rgba(148, 163, 184, 0.05)', drawBorder: false },
                        position: 'left',
                        title: {
                            display: !!chartData.yAxisTitle,
                            text: chartData.yAxisTitle,
                            color: '#94a3b8',
                            font: { size: 11 }
                        }
                    },
                    y1: chartData.is_dual_axis ? {
                        beginAtZero: true,
                        position: 'right',
                        ticks: {
                            color: '#f43f5e',
                            font: { family: 'Inter' },
                            stepSize: chartData.is_rating ? 1 : undefined // Force integer steps for ratings
                        },
                        min: chartData.is_rating ? 0 : undefined,
                        max: chartData.is_rating ? 5 : undefined,
                        grid: { drawOnChartArea: false },
                        title: {
                            display: !!chartData.y1AxisTitle,
                            text: chartData.y1AxisTitle,
                            color: '#f43f5e',
                            font: { size: 11 }
                        }
                    } : undefined,
                    x: {
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } },
                        grid: { display: false }
                    }
                } : {})
            }
        };

        new Chart(ctx, config);
    } catch (error) {
        console.error('Error rendering chart:', error);
        // Show error on canvas container
        const container = canvas.parentElement;
        container.innerHTML = `<div style="padding: 20px; color: #ef4444; text-align: center;">
            <p>⚠️ Gagal menampilkan grafik</p>
            <small>${error.message}</small>
        </div>`;
    }
}

// Download CSV
function downloadCSV(queryIndex) {
    try {
        // Open CSV export endpoint in new tab
        const url = `/api/export/csv/${queryIndex}?user_id=${userId}`;
        window.open(url, '_blank');
    } catch (error) {
        console.error('Error downloading CSV:', error);
        alert('Failed to download CSV. Please try again.');
    }
}

// Add error message
function addErrorMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `<strong>❌ Error:</strong><br>${escapeHtml(message)}`;
    contentDiv.appendChild(errorDiv);

    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Remove message by ID
function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}
