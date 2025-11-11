/**
 * Git Analysis JavaScript
 * Handles charts and interactivity for the Git Analysis page
 */

class GitAnalysis {
    constructor() {
        this.data = {};
        this.init();
    }

    init() {
        this.loadData();
        this.setupCharts();
        this.setupInteractivity();
    }

    loadData() {
        try {
            // Load git statistics from embedded data
            if (window.GIT_STATS_DATA) {
                this.data.gitStats = this.formatGitCommitsData(window.GIT_STATS_DATA);
            }
            
            // Load git churn data from embedded data
            if (window.GIT_CHURN_DATA) {
                this.data.gitChurn = window.GIT_CHURN_DATA;
            }
            
            // Load comprehensive git analysis data
            if (window.GIT_ANALYSIS_DATA) {
                this.data.analysis = window.GIT_ANALYSIS_DATA;
                this.populateAnalysisData();
            }
            
            console.log('Git analysis data loaded successfully');
        } catch (error) {
            console.error('Error loading git analysis data:', error);
        }
    }

    formatGitCommitsData(gitData) {
        // Convert git statistics data to chart format
        if (gitData && typeof gitData === 'object' && !Array.isArray(gitData)) {
            return Object.entries(gitData).map(([date, count]) => ({
                month: this.formatMonthName(date),
                commits: count,
                date: new Date(date + '-01').toISOString()
            })).sort((a, b) => new Date(a.date) - new Date(b.date));
        }
        return [];
    }

    formatMonthName(monthString) {
        try {
            let date;
            if (monthString.includes('-')) {
                date = new Date(monthString + (monthString.split('-').length === 2 ? '-01' : ''));
            } else {
                date = new Date(monthString);
            }
            
            return date.toLocaleDateString('en-US', { 
                month: 'short', 
                year: 'numeric' 
            });
        } catch (error) {
            return monthString; // Return original if parsing fails
        }
    }

    setupCharts() {
        this.setupCommitChart();
        this.setupChurnChart();
    }

    setupCommitChart() {
        const canvas = document.getElementById('gitCommitsChart');
        if (!canvas || !this.data.gitStats || this.data.gitStats.length === 0) {
            return;
        }

        const ctx = canvas.getContext('2d');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.data.gitStats.map(item => item.month),
                datasets: [{
                    label: 'Commits',
                    data: this.data.gitStats.map(item => item.commits),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            color: '#64748b'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            color: '#64748b'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#3b82f6',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: (context) => `${context[0].label}`,
                            label: (context) => `${context.parsed.y} commits`
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    setupChurnChart() {
        const canvas = document.getElementById('gitChurnChart');
        if (!canvas || !this.data.gitChurn) {
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Sample churn data if not provided
        const churnData = this.data.gitChurn || this.generateSampleChurnData();
        
        const labels = Object.keys(churnData);
        const added = labels.map(label => churnData[label].added);
        const removed = labels.map(label => -churnData[label].removed);
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Lines Removed',
                        data: removed, // Goes downward
                        backgroundColor: 'rgba(255, 99, 132, 0.6)'
                    },
                    {
                        label: 'Lines Added',
                        data: added, // Goes upward
                        backgroundColor: 'rgba(75, 192, 192, 0.6)'
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${Math.abs(context.raw)}`;
                        }
                    }
                }
                },
                scales: {
                    y: {
                        stacked: true,
                        ticks: {
                            callback: function(value) {
                                return Math.abs(value);
                            }
                        },
                    },
                    x: {
                        stacked: true
                    }
            
                }
            }
        });
    }

    generateSampleChurnData() {
        // Generate sample data if churn data is not provided
        const months = [];
        const added = [];
        const removed = [];
        
        // Get last 6 months
        for (let i = 5; i >= 0; i--) {
            const date = new Date();
            date.setMonth(date.getMonth() - i);
            months.push(date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }));
            
            // Generate random but realistic data
            added.push(Math.floor(Math.random() * 2000) + 500);
            removed.push(Math.floor(Math.random() * 1500) + 200);
        }
        
        return {
            labels: months,
            added: added,
            removed: removed
        };
    }

    populateAnalysisData() {
        if (!this.data.analysis) return;
        
        try {
            this.populateActiveDays();
            this.populateCommitQuality();
            this.populateRecommendations();
            
            // Setup table interactivity after populating tables
            this.setupTableInteractivity();
        } catch (error) {
            console.error('Error populating analysis data:', error);
        }
    }

    populateActiveDays() {
        const container = document.getElementById('active-days-content');
        if (!container || !this.data.analysis.active_days) return;
        
        container.innerHTML = '';
        
        this.data.analysis.active_days.forEach(day => {
            const p = document.createElement('p');
            const note = day.is_deploy_day ? ` (${day.note})` : '';
            p.innerHTML = `<strong>${day.day_name}:</strong> ${day.percentage}% of commits${note}`;
            container.appendChild(p);
        });
    }

    populateCommitQuality() {
        const container = document.getElementById('commit-quality-content');
        if (!container || !this.data.analysis) return;
        
        container.innerHTML = `
            <p><strong>Small commits:</strong> ${this.data.analysis.small_commits_percentage}% (&lt;50 lines)</p>
            <p><strong>Message quality:</strong> ${this.data.analysis.good_message_percentage}% have good descriptions</p>
            <p><strong>Fix commits:</strong> ${this.data.analysis.fix_commits_percentage}% (indicates stability)</p>
        `;
    }

    populateRecommendations() {
        const container = document.getElementById('recommendations-content');
        if (!container || !this.data.analysis.recommendations) return;
        
        container.innerHTML = '';
        
        this.data.analysis.recommendations.forEach(rec => {
            const p = document.createElement('p');
            p.textContent = `• ${rec.recommendation}`;
            container.appendChild(p);
        });
    }

    setupInteractivity() {
        // Setup navigation highlight
        this.setupNavigationHighlight();
        // Table interactivity is set up after populating tables in populateAnalysisData()
    }

    setupTableInteractivity() {
        const tables = document.querySelectorAll('.hotspot-table tbody tr, .contributor-table tbody tr');
        tables.forEach(row => {
            row.style.cursor = 'pointer';
            row.addEventListener('click', function() {
                // Highlight clicked row
                this.style.backgroundColor = 'var(--bg-tertiary)';
                setTimeout(() => {
                    this.style.backgroundColor = '';
                }, 300);
            });
            
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(59, 130, 246, 0.05)';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
    }

    setupNavigationHighlight() {
        // Ensure git analysis nav item is highlighted
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            const link = item.querySelector('.nav-link');
            if (link && link.getAttribute('href') === 'git_analysis.html') {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    // Utility function to show notifications
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            color: white;
            font-weight: 500;
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;

        // Set background color based on type
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        notification.textContent = message;

        // Add to DOM
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Remove after delay
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize git analysis when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.gitAnalysis = new GitAnalysis();
});

// Export for global access
window.GitAnalysis = GitAnalysis;
