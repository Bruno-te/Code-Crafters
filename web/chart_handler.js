// Dashboard Chart Handler and Data Management
class MoMoDashboard {
    constructor() {
        this.charts = {};
        this.data = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadData();
        this.initializeCharts();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Search and filters
        document.getElementById('search-transactions').addEventListener('input', (e) => {
            this.filterTransactions(e.target.value);
        });

        document.getElementById('category-filter').addEventListener('change', (e) => {
            this.filterTransactions(document.getElementById('search-transactions').value, e.target.value);
        });

        document.getElementById('date-filter').addEventListener('change', (e) => {
            this.filterTransactions(document.getElementById('search-transactions').value, 
                                 document.getElementById('category-filter').value, e.target.value);
        });

        // Report generation
        document.getElementById('generate-report').addEventListener('click', () => {
            this.generateReport();
        });
    }

    switchTab(tabName) {
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        // Refresh charts if needed
        if (tabName === 'analytics') {
            this.refreshAnalyticsCharts();
        }
    }

    async loadData() {
        try {
            // In a real application, this would fetch from your API
            // For now, we'll use sample data
            const response = await fetch('data/processed/dashboard.json');
            if (response.ok) {
                this.data = await response.json();
            } else {
                // Fallback to sample data
                this.data = this.getSampleData();
            }
            this.updateDashboard();
        } catch (error) {
            console.log('Using sample data:', error);
            this.data = this.getSampleData();
            this.updateDashboard();
        }
    }

    getSampleData() {
        return {
            summary: {
                totalTransactions: 15420,
                totalAmount: 2847500,
                successRate: 94.2,
                activeUsers: 3240
            },
            transactions: this.generateSampleTransactions(),
            analytics: {
                volumeByDate: this.generateVolumeData(),
                categoryDistribution: this.generateCategoryData(),
                hourlyPattern: this.generateHourlyData(),
                amountDistribution: this.generateAmountData(),
                geographicData: this.generateGeoData(),
                successTrend: this.generateSuccessTrendData()
            }
        };
    }

    generateSampleTransactions() {
        const categories = ['payment', 'transfer', 'withdrawal', 'deposit'];
        const statuses = ['success', 'pending', 'failed'];
        const transactions = [];

        for (let i = 1; i <= 100; i++) {
            transactions.push({
                id: `TXN${String(i).padStart(6, '0')}`,
                date: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
                amount: Math.floor(Math.random() * 10000) + 100,
                category: categories[Math.floor(Math.random() * categories.length)],
                status: statuses[Math.floor(Math.random() * statuses.length)],
                phone: `+233${Math.floor(Math.random() * 90000000) + 10000000}`
            });
        }
        return transactions;
    }

    generateVolumeData() {
        const data = [];
        const now = new Date();
        for (let i = 30; i >= 0; i--) {
            const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
            data.push({
                date: date.toISOString().split('T')[0],
                volume: Math.floor(Math.random() * 500) + 100
            });
        }
        return data;
    }

    generateCategoryData() {
        return [
            { category: 'Payment', count: 45, amount: 1200000 },
            { category: 'Transfer', count: 30, amount: 800000 },
            { category: 'Withdrawal', count: 15, amount: 400000 },
            { category: 'Deposit', count: 10, amount: 447500 }
        ];
    }

    generateHourlyData() {
        const data = [];
        for (let hour = 0; hour < 24; hour++) {
            data.push({
                hour: hour,
                transactions: Math.floor(Math.random() * 100) + 20
            });
        }
        return data;
    }

    generateAmountData() {
        return [
            { range: '0-1000', count: 40 },
            { range: '1001-5000', count: 35 },
            { range: '5001-10000', count: 15 },
            { range: '10001+', count: 10 }
        ];
    }

    generateGeoData() {
        return [
            { region: 'Greater Accra', count: 45 },
            { region: 'Ashanti', count: 25 },
            { region: 'Western', count: 15 },
            { region: 'Central', count: 10 },
            { region: 'Others', count: 5 }
        ];
    }

    generateSuccessTrendData() {
        const data = [];
        const now = new Date();
        for (let i = 30; i >= 0; i--) {
            const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
            data.push({
                date: date.toISOString().split('T')[0],
                rate: 90 + Math.random() * 8
            });
        }
        return data;
    }

    updateDashboard() {
        if (!this.data) return;

        // Update summary stats
        document.getElementById('total-transactions').textContent = this.data.summary.totalTransactions.toLocaleString();
        document.getElementById('total-amount').textContent = `$${(this.data.summary.totalAmount / 1000).toFixed(1)}K`;
        document.getElementById('success-rate').textContent = `${this.data.summary.successRate}%`;
        document.getElementById('active-users').textContent = this.data.summary.activeUsers.toLocaleString();

        // Populate transactions table
        this.populateTransactionsTable(this.data.transactions);
    }

    populateTransactionsTable(transactions) {
        const tbody = document.getElementById('transactions-tbody');
        tbody.innerHTML = '';

        transactions.forEach(txn => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${txn.id}</td>
                <td>${new Date(txn.date).toLocaleDateString()}</td>
                <td>$${txn.amount.toLocaleString()}</td>
                <td><span class="category-badge ${txn.category}">${txn.category}</span></td>
                <td><span class="status-badge ${txn.status}">${txn.status}</span></td>
                <td>${txn.phone}</td>
            `;
            tbody.appendChild(row);
        });
    }

    filterTransactions(searchTerm = '', category = '', date = '') {
        let filtered = this.data.transactions;

        if (searchTerm) {
            filtered = filtered.filter(txn => 
                txn.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                txn.phone.includes(searchTerm)
            );
        }

        if (category) {
            filtered = filtered.filter(txn => txn.category === category);
        }

        if (date) {
            filtered = filtered.filter(txn => 
                txn.date.startsWith(date)
            );
        }

        this.populateTransactionsTable(filtered);
    }

    initializeCharts() {
        this.createVolumeChart();
        this.createCategoryChart();
        this.createAmountDistributionChart();
        this.createHourlyPatternChart();
        this.createGeoChart();
        this.createSuccessTrendChart();
    }

    createVolumeChart() {
        const ctx = document.getElementById('volume-chart').getContext('2d');
        this.charts.volume = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.data.analytics.volumeByDate.map(d => d.date),
                datasets: [{
                    label: 'Transaction Volume',
                    data: this.data.analytics.volumeByDate.map(d => d.volume),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createCategoryChart() {
        const ctx = document.getElementById('category-chart').getContext('2d');
        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.data.analytics.categoryDistribution.map(d => d.category),
                datasets: [{
                    data: this.data.analytics.categoryDistribution.map(d => d.count),
                    backgroundColor: [
                        '#667eea',
                        '#f093fb',
                        '#f5576c',
                        '#4ade80'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    createAmountDistributionChart() {
        const ctx = document.getElementById('amount-distribution-chart').getContext('2d');
        this.charts.amountDistribution = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.data.analytics.amountDistribution.map(d => d.range),
                datasets: [{
                    label: 'Transaction Count',
                    data: this.data.analytics.amountDistribution.map(d => d.count),
                    backgroundColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createHourlyPatternChart() {
        const ctx = document.getElementById('hourly-pattern-chart').getContext('2d');
        this.charts.hourlyPattern = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.data.analytics.hourlyPattern.map(d => `${d.hour}:00`),
                datasets: [{
                    label: 'Transactions',
                    data: this.data.analytics.hourlyPattern.map(d => d.transactions),
                    backgroundColor: '#f093fb'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createGeoChart() {
        const ctx = document.getElementById('geo-chart').getContext('2d');
        this.charts.geo = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: this.data.analytics.geographicData.map(d => d.region),
                datasets: [{
                    data: this.data.analytics.geographicData.map(d => d.count),
                    backgroundColor: [
                        '#667eea',
                        '#f093fb',
                        '#f5576c',
                        '#4ade80',
                        '#fbbf24'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    createSuccessTrendChart() {
        const ctx = document.getElementById('success-trend-chart').getContext('2d');
        this.charts.successTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.data.analytics.successTrend.map(d => d.date),
                datasets: [{
                    label: 'Success Rate (%)',
                    data: this.data.analytics.successTrend.map(d => d.rate),
                    borderColor: '#4ade80',
                    backgroundColor: 'rgba(74, 222, 128, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 80,
                        max: 100
                    }
                }
            }
        });
    }

    refreshAnalyticsCharts() {
        // Refresh analytics charts when switching to analytics tab
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.resize();
            }
        });
    }

    generateReport() {
        const reportType = document.getElementById('report-type').value;
        const startDate = document.getElementById('report-start-date').value;
        const endDate = document.getElementById('report-end-date').value;

        let reportContent = '';

        switch (reportType) {
            case 'daily':
                reportContent = this.generateDailyReport();
                break;
            case 'weekly':
                reportContent = this.generateWeeklyReport();
                break;
            case 'monthly':
                reportContent = this.generateMonthlyReport();
                break;
            case 'custom':
                if (startDate && endDate) {
                    reportContent = this.generateCustomReport(startDate, endDate);
                } else {
                    reportContent = '<p class="error">Please select start and end dates for custom report.</p>';
                }
                break;
        }

        document.getElementById('report-output').innerHTML = reportContent;
    }

    generateDailyReport() {
        const today = new Date().toLocaleDateString();
        return `
            <h4>Daily Report - ${today}</h4>
            <div class="report-stats">
                <p><strong>Total Transactions:</strong> ${this.data.summary.totalTransactions}</p>
                <p><strong>Total Amount:</strong> $${this.data.summary.totalAmount.toLocaleString()}</p>
                <p><strong>Success Rate:</strong> ${this.data.summary.successRate}%</p>
                <p><strong>Active Users:</strong> ${this.data.summary.activeUsers}</p>
            </div>
        `;
    }

    generateWeeklyReport() {
        return `
            <h4>Weekly Report</h4>
            <div class="report-stats">
                <p><strong>Average Daily Transactions:</strong> ${Math.round(this.data.summary.totalTransactions / 7)}</p>
                <p><strong>Weekly Volume:</strong> $${this.data.summary.totalAmount.toLocaleString()}</p>
                <p><strong>Trend:</strong> 📈 Increasing</p>
            </div>
        `;
    }

    generateMonthlyReport() {
        return `
            <h4>Monthly Report</h4>
            <div class="report-stats">
                <p><strong>Monthly Transactions:</strong> ${this.data.summary.totalTransactions}</p>
                <p><strong>Monthly Volume:</strong> $${this.data.summary.totalAmount.toLocaleString()}</p>
                <p><strong>Growth Rate:</strong> +15.3%</p>
            </div>
        `;
    }

    generateCustomReport(startDate, endDate) {
        return `
            <h4>Custom Report: ${startDate} to ${endDate}</h4>
            <div class="report-stats">
                <p><strong>Date Range:</strong> ${startDate} - ${endDate}</p>
                <p><strong>Transactions in Range:</strong> ${Math.floor(this.data.summary.totalTransactions * 0.3)}</p>
                <p><strong>Amount in Range:</strong> $${Math.floor(this.data.summary.totalAmount * 0.3).toLocaleString()}</p>
            </div>
        `;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MoMoDashboard();
});

// Add some CSS for badges
const style = document.createElement('style');
style.textContent = `
    .category-badge, .status-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: capitalize;
    }
    
    .category-badge.payment { background: #dbeafe; color: #1e40af; }
    .category-badge.transfer { background: #fef3c7; color: #d97706; }
    .category-badge.withdrawal { background: #fecaca; color: #dc2626; }
    .category-badge.deposit { background: #d1fae5; color: #059669; }
    
    .status-badge.success { background: #d1fae5; color: #059669; }
    .status-badge.pending { background: #fef3c7; color: #d97706; }
    .status-badge.failed { background: #fecaca; color: #dc2626; }
    
    .report-stats p {
        margin: 10px 0;
        padding: 8px;
        background: #f8fafc;
        border-radius: 6px;
    }
    
    .error {
        color: #dc2626;
        font-weight: 500;
    }
`;
document.head.appendChild(style);
