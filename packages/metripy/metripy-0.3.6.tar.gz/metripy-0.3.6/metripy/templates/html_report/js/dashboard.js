/**
 * Dashboard JavaScript
 * Handles main dashboard functionality, navigation, and data management
 */

class Dashboard {
    constructor() {
        this.data = {};
        this.currentSection = 'overview';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadData();
        this.updateMetrics();
        //this.setupNavigation();
        this.setupResponsiveMenu();
    }

    setupEventListeners() {
        // Navigation links
        /*document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNavigation(e.target.closest('.nav-link'));
            });
        });*/

        // Header action buttons removed

        // Chart period controls removed - showing all data

        // Window resize handler
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            const link = item.querySelector('.nav-link');
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active class from all items
                navItems.forEach(navItem => navItem.classList.remove('active'));
                
                // Add active class to clicked item
                item.classList.add('active');
                
                // Update current section
                const href = link.getAttribute('href');
                this.currentSection = href.replace('#', '');
                
                // Smooth scroll or section switching logic can go here
                this.switchSection(this.currentSection);
            });
        });
    }

    setupResponsiveMenu() {
        // Mobile menu toggle logic
        const createMenuToggle = () => {
            if (window.innerWidth <= 1024 && !document.querySelector('.menu-toggle')) {
                const toggle = document.createElement('button');
                toggle.className = 'menu-toggle';
                toggle.innerHTML = '<i class="fas fa-bars"></i>';
                toggle.addEventListener('click', () => {
                    document.querySelector('.sidebar').classList.toggle('open');
                });
                
                document.querySelector('.page-header').prepend(toggle);
            }
        };

        createMenuToggle();
        window.addEventListener('resize', createMenuToggle);
    }

    handleNavigation(link) {
        const href = link.getAttribute('href');
        const section = href.replace('#', '');
        
        // Update active navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        link.closest('.nav-item').classList.add('active');
        
        // Switch to section
        this.switchSection(section);
    }

    switchSection(section) {
        console.log(`Switching to section: ${section}`);
        
        // Here you can implement section switching logic
        // For now, we'll just update the page title
        const titles = {
            overview: 'Code Metrics Overview',
            files: 'File Analysis',
            complexity: 'Complexity Analysis',
            maintainability: 'Maintainability Report',
            'git-analysis': 'Git Analysis',
            trends: 'Trend Analysis'
        };
        
        const titleElement = document.querySelector('.page-header h1');
        if (titleElement && titles[section]) {
            titleElement.textContent = titles[section];
        }
        
        this.currentSection = section;
        this.loadSectionData(section);
    }

    loadSectionData(section) {
        // Load section-specific data
        switch (section) {
            case 'overview':
                this.updateMetrics();
                break;
            case 'files':
                this.loadFilesList();
                break;
            case 'complexity':
                this.loadComplexityData();
                break;
            case 'maintainability':
                this.loadMaintainabilityData();
                break;
            case 'git-analysis':
                this.loadGitAnalysis();
                break;
            case 'trends':
                this.loadTrendsData();
                break;
        }
    }

    async loadData() {
        try {
            // Load git statistics from embedded data
            await this.loadGitStatistics();
            
            // Load metrics data from embedded template data
            if (window.METRICS_DATA) {
                this.data = {
                    ...this.data,
                    ...window.METRICS_DATA
                };
                console.log('Loaded metrics data from template');
                
                // Update the UI with the loaded data
                this.updateMetrics();
            } else {
                console.warn('METRICS_DATA not found in template, using fallback');
                await this.simulateDataLoading(); // Fallback for development
                this.updateMetrics();
            }
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async loadGitStatistics() {
        try {
            // Check if git stats data is embedded in the page
            if (window.GIT_STATS_DATA) {
                console.log('Loading git statistics from embedded data');
                this.data.gitCommits = this.formatGitCommitsData(window.GIT_STATS_DATA);
            } else {
                throw new Error('No git statistics data found. Please ensure git_stats.json data is embedded in the HTML template.');
            }
            
        } catch (error) {
            console.error('Failed to load git statistics:', error);
            this.showError('Failed to load git statistics: ' + error.message);
            // Set empty data instead of fallback
            this.data.gitCommits = [];
        }
    }

    formatGitCommitsData(gitData) {
        // Convert git statistics data to chart format
        // Expected format: { "2024-01": 42, "2024-02": 38, ... }
        if (gitData && typeof gitData === 'object' && !Array.isArray(gitData)) {
            return Object.entries(gitData).map(([date, count]) => ({
                month: this.formatMonthName(date),
                commits: count,
                date: new Date(date + '-01').toISOString()
            })).sort((a, b) => new Date(a.date) - new Date(b.date));
        } else {
            // No valid data format
            console.error('Git data format not recognized');
            throw new Error('Invalid git statistics data format. Expected: {"2024-01": 42, "2024-02": 38, ...}');
        }
    }

    formatMonthName(monthString) {
        try {
            // Handle different date formats
            let date;
            if (monthString.includes('-')) {
                // Format: "2024-10" or "2024-10-01"
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

    simulateDataLoading() {
        return new Promise(resolve => {
            setTimeout(() => {
                // Preserve gitCommits data if already loaded from JSON
                const existingGitCommits = this.data.gitCommits;
                
                // Load data from external metrics file if available
                if (window.METRICS_DATA) {
                    this.data = {
                        ...this.data, // Preserve existing data
                        ...window.METRICS_DATA, // Load metrics from external file
                        gitCommits: existingGitCommits || [] // Preserve git data
                    };
                } else {
                    // Fallback to sample data if external data not available
                    console.warn('METRICS_DATA not found, using fallback sample data');
                    this.data = {
                        ...this.data,
                        totalLoc: 15420,
                        avgComplexity: 2.8,
                        maintainabilityIndex: 78.5,
                        avgMethodSize: 12.3,
                        gitCommits: existingGitCommits || [],
                        segmentation: {
                            loc: { good: 45, ok: 32, warning: 18, critical: 5 },
                            complexity: { good: 52, ok: 28, warning: 15, critical: 5 },
                            maintainability: { good: 35, ok: 42, warning: 18, critical: 5 },
                            methodSize: { good: 48, ok: 35, warning: 12, critical: 5 }
                        }
                    };
                }
                resolve();
            }, 500);
        });
    }


    updateMetrics() {
        if (!this.data.totalLoc) return;

        // Update metric values with animation
        this.animateValue('total-loc', this.data.totalLoc);
        this.animateValue('avg-complexity', this.data.avgComplexity, 1);
        this.animateValue('maintainability-index', this.data.maintainabilityIndex, 1);
        this.animateValue('avg-method-size', this.data.avgMethodSize, 1);

        // Complex files and recent analysis sections removed
        
        // Update segmentations
        this.updateSegmentations();
    }

    animateValue(elementId, targetValue, decimals = 0) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = 0;
        const duration = 2000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            
            const currentValue = startValue + (targetValue - startValue) * easeOutQuart;
            element.textContent = currentValue.toFixed(decimals);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }


    updateSegmentations() {
        if (!this.data.segmentation) {
            console.warn('No segmentation data found');
            return;
        }

        // Update LOC segmentation
        this.updateSegmentation('loc', this.data.segmentation.loc);
        
        // Update Complexity segmentation
        this.updateSegmentation('complexity', this.data.segmentation.complexity);
        
        // Update Maintainability segmentation
        this.updateSegmentation('maintainability', this.data.segmentation.maintainability);
        
        // Update Method Size segmentation
        this.updateSegmentation('methodSize', this.data.segmentation.methodSize);
    }

    updateSegmentation(metricType, segmentData) {
        // Calculate total files to determine percentages
        const total = Object.values(segmentData).reduce((sum, count) => sum + count, 0);
        
        if (total === 0) return; // No data to display
        
        
        // Get display mapping for this metric type
        const displayMapping = this.getDisplayMapping(metricType);
        const segmentOrder = this.getSegmentOrder(metricType);
        
        // Calculate all percentages first to ensure they add up to 100%
        let percentages = [];
        let totalPercentage = 0;
        
        segmentOrder.forEach(dataCategory => {
            const count = segmentData[dataCategory] || 0;
            const percentage = (count / total) * 100;
            percentages.push(percentage);
            totalPercentage += percentage;
        });
        
        // Adjust for any rounding errors to ensure total is exactly 100%
        if (totalPercentage > 0 && totalPercentage !== 100) {
            const adjustment = 100 / totalPercentage;
            percentages = percentages.map(p => p * adjustment);
        }
        
        segmentOrder.forEach((dataCategory, index) => {
            const count = segmentData[dataCategory] || 0;
            const percentage = percentages[index];
            
            // Get the display name for DOM queries
            const displayName = displayMapping[dataCategory] || dataCategory;
            
            
            // Update segment bar width
            const segmentElement = document.querySelector(`[data-segment="${displayName}"]`);
            
            if (segmentElement) {
                if (count === 0) {
                    // Hide segments with no data
                    segmentElement.style.width = '0%';
                    segmentElement.style.minWidth = '0px';
                    segmentElement.removeAttribute('title');
                } else {
                    segmentElement.style.width = `${percentage.toFixed(2)}%`;
                    // Only apply min-width for very small but non-zero segments
                    segmentElement.style.minWidth = percentage < 0.5 ? '1px' : '0px';
                }
            }
            
            // Update count display and add tooltip to the label
            const countElement = document.querySelector(`[data-count="${displayName}"]`);
            if (countElement) {
                countElement.textContent = count;
                
                // Add tooltip to the parent segment-label for better hover area
                const segmentLabel = countElement.closest('.segment-label');
                if (segmentLabel) {
                    const tooltipText = this.getTooltipText(metricType, dataCategory, count);
                    if (tooltipText) {
                        segmentLabel.setAttribute('title', tooltipText);
                    }
                }
            }
        });
    }

    getSegmentOrder(metricType) {
        // Use consistent naming across all metrics: good, ok, warning, critical
        return ['good', 'ok', 'warning', 'critical'];
    }

    // Map data categories to display names for each metric type
    getDisplayMapping(metricType) {
        const displayMap = {
            loc: {
                'good': 'small',
                'ok': 'medium', 
                'warning': 'large',
                'critical': 'very-large'
            },
            complexity: {
                'good': 'simple',
                'ok': 'moderate',
                'warning': 'complex', 
                'critical': 'very-complex'
            },
            maintainability: {
                'good': 'excellent',
                'ok': 'good',
                'warning': 'fair',
                'critical': 'poor'
            },
            methodSize: {
                'good': 'concise',
                'ok': 'optimal',
                'warning': 'large',
                'critical': 'too-large'
            }
        };
        return displayMap[metricType] || {};
    }

    getTooltipText(metricType, dataCategory, count) {
        const tooltipMap = {
            loc: {
                'good': `${count} files with 1-200 lines of code (easy to understand and maintain)`,
                'ok': `${count} files with 201-500 lines of code (reasonable size, manageable)`,
                'warning': `${count} files with 501-1000 lines of code (consider splitting into modules)`,
                'critical': `${count} files with 1000+ lines of code (urgent refactoring needed)`
            },
            complexity: {
                'good': `${count} files with 1-5 average cyclomatic complexity (easy to test and maintain)`,
                'ok': `${count} files with 6-10 average cyclomatic complexity (acceptable complexity)`,
                'warning': `${count} files with 11-20 average cyclomatic complexity (should consider refactoring)`,
                'critical': `${count} files with 21+ average cyclomatic complexity (high risk, urgent attention needed)`
            },
            maintainability: {
                'good': `${count} files with 80-100 maintainability score (highly maintainable code)`,
                'ok': `${count} files with 60-79 maintainability score (well-maintained, minor improvements)`,
                'warning': `${count} files with 40-59 maintainability score (needs attention and cleanup)`,
                'critical': `${count} files with 0-39 maintainability score (critical refactoring required)`
            },
            methodSize: {
                'good': `${count} files with 1-15 average lines per method (well-focused methods)`,
                'ok': `${count} files with 16-30 average lines per method (good balance of functionality)`,
                'warning': `${count} files with 31-50 average lines per method (consider breaking down)`,
                'critical': `${count} files with 51+ average lines per method (should be split immediately)`
            }
        };

        return tooltipMap[metricType]?.[dataCategory] || '';
    }


    loadComplexityData() {
        console.log('Loading complexity data...');
        // Implement complexity data loading
    }

    loadMaintainabilityData() {
        console.log('Loading maintainability data...');
        // Implement maintainability data loading
    }

    loadGitAnalysis() {
        console.log('Loading git analysis...');
        // Implement git analysis loading
    }

    loadTrendsData() {
        console.log('Loading trends data...');
        // Implement trends data loading
    }

    handleResize() {
        // Handle responsive behavior
        if (window.innerWidth > 1024) {
            document.querySelector('.sidebar')?.classList.remove('open');
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Create notification element
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
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Export for global access
window.Dashboard = Dashboard;
