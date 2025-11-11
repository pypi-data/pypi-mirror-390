/**
 * Charts JavaScript
 * Handles Chart.js functionality for git commits visualization and other charts
 */

class ChartManager {
    constructor() {
        this.charts = {};
        this.data = {};
        this.colors = {
            primary: '#3b82f6',
            primaryGradient: {
                start: 'rgba(59, 130, 246, 0.8)',
                end: 'rgba(59, 130, 246, 0.1)'
            },
            success: '#10b981',
            warning: '#f59e0b',
            danger: '#ef4444',
            info: '#06b6d4',
            text: '#1e293b',
            textSecondary: '#64748b',
            border: '#e2e8f0'
        };
        this.init();
    }

    init() {
        this.setupChartDefaults();
        this.initializeCharts();
    }

    setupChartDefaults() {
        // Configure Chart.js global defaults
        Chart.defaults.font.family = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        Chart.defaults.font.size = 12;
        Chart.defaults.color = this.colors.textSecondary;
        Chart.defaults.borderColor = this.colors.border;
        Chart.defaults.backgroundColor = this.colors.primary;
        
        // Configure responsive defaults
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        
        // Configure animation defaults
        /*
        This had the consequence of hindering license chart rendering
        Chart.defaults.animation = {
            duration: 1000,
            easing: 'easeOutQuart'
        };
        */
    }

    initializeCharts() {
        // Wait for DOM to be ready and data to be available
        this.waitForData().then(() => {
            this.createGitCommitsChart();
            // Add more chart initializations here as needed
        });
    }

    waitForData() {
        return new Promise((resolve) => {
            const checkData = () => {
                if (window.dashboard && window.dashboard.data && window.dashboard.data.gitCommits) {
                    this.data = window.dashboard.data;
                    console.log('Git commits data loaded:', this.data.gitCommits.length, 'months');
                    resolve();
                } else {
                    setTimeout(checkData, 100);
                }
            };
            checkData();
        });
    }

    createGitCommitsChart() {
        const canvas = document.getElementById('gitCommitsChart');
        if (!canvas) {
            console.warn('Git commits chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Prepare data for the chart
        const chartData = this.prepareGitCommitsData();
        
        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, this.colors.primaryGradient.start);
        gradient.addColorStop(1, this.colors.primaryGradient.end);

        this.charts.gitCommits = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Commits',
                    data: chartData.values,
                    borderColor: this.colors.primary,
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: this.colors.primary,
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        titleFont: {
                            size: 14,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 13
                        },
                        padding: 12,
                        callbacks: {
                            title: (context) => {
                                return context[0].label;
                            },
                            label: (context) => {
                                const value = context.parsed.y;
                                const plural = value === 1 ? 'commit' : 'commits';
                                return `${value} ${plural}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        },
                        border: {
                            display: false
                        },
                        ticks: {
                            color: this.colors.textSecondary,
                            font: {
                                size: 11,
                                weight: '500'
                            },
                            maxRotation: 0,
                            padding: 10
                        }
                    },
                    y: {
                        display: true,
                        beginAtZero: true,
                        grid: {
                            color: this.colors.border,
                            drawBorder: false
                        },
                        border: {
                            display: false
                        },
                        ticks: {
                            color: this.colors.textSecondary,
                            font: {
                                size: 11,
                                weight: '500'
                            },
                            padding: 10,
                            callback: function(value) {
                                if (value === 0) return '0';
                                return value % 1 === 0 ? value : '';
                            }
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuint'
                },
                elements: {
                    point: {
                        hoverRadius: 8
                    }
                }
            }
        });

        // Add chart resize handler
        this.addResizeHandler('gitCommits');
    }

    prepareGitCommitsData() {
        if (!this.data.gitCommits) return { labels: [], values: [] };

        const data = [...this.data.gitCommits];

        return {
            labels: data.map(item => item.month),
            values: data.map(item => item.commits)
        };
    }


    updateData(newData) {
        this.data.gitCommits = newData;
        
        if (this.charts.gitCommits) {
            const chartData = this.prepareGitCommitsData();
            
            this.charts.gitCommits.data.labels = chartData.labels;
            this.charts.gitCommits.data.datasets[0].data = chartData.values;
            
            this.charts.gitCommits.update('active');
        }
    }

    addResizeHandler(chartName) {
        if (!this.charts[chartName]) return;

        const resizeObserver = new ResizeObserver(entries => {
            this.charts[chartName].resize();
        });

        const canvas = this.charts[chartName].canvas;
        if (canvas && canvas.parentElement) {
            resizeObserver.observe(canvas.parentElement);
        }
    }

    destroyChart(chartName) {
        if (this.charts[chartName]) {
            this.charts[chartName].destroy();
            delete this.charts[chartName];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartName => {
            this.destroyChart(chartName);
        });
    }

    // Utility methods
    hexToRgba(hex, alpha = 1) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        if (!result) return null;
        
        const r = parseInt(result[1], 16);
        const g = parseInt(result[2], 16);
        const b = parseInt(result[3], 16);
        
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
}

// Initialize chart manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chartManager = new ChartManager();
});

// Handle page visibility changes to pause/resume animations
document.addEventListener('visibilitychange', () => {
    if (window.chartManager) {
        Object.values(window.chartManager.charts).forEach(chart => {
            if (document.hidden) {
                chart.stop();
            } else {
                chart.update('none');
            }
        });
    }
});

// Handle window beforeunload to cleanup
window.addEventListener('beforeunload', () => {
    if (window.chartManager) {
        window.chartManager.destroyAllCharts();
    }
});

// Export for global access
window.ChartManager = ChartManager;
