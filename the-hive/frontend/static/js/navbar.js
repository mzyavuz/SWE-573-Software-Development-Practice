/**
 * Shared Navigation Bar Module
 * This module handles navigation rendering across all pages
 */

const NavBar = {
    /**
     * Initialize and render the navigation bar
     * @param {string} activePage - The current active page ('home', 'services', 'my-services', 'messages', 'profile')
     */
    async init(activePage = '') {
        return new Promise((resolve, reject) => {
            const token = localStorage.getItem('access_token');
            const navButtons = document.getElementById('nav-buttons');
            
            if (!navButtons) {
                console.error('Navigation container #nav-buttons not found');
                reject(new Error('Navigation container not found'));
                return;
            }
            
            if (token) {
                this.renderAuthenticatedNav(navButtons, activePage).then(() => {
                    // Setup dropdown after rendering
                    this.setupDropdown();
                    // Small delay to ensure DOM is updated
                    setTimeout(() => resolve(), 10);
                }).catch(reject);
            } else {
                this.renderGuestNav(navButtons);
                setTimeout(() => resolve(), 10);
            }
        });
    },

    /**
     * Render navigation for authenticated users
     */
    async renderAuthenticatedNav(navButtons, activePage) {
        try {
            const userData = JSON.parse(localStorage.getItem('user') || '{}');
            const initials = userData.first_name && userData.last_name 
                ? (userData.first_name[0] + userData.last_name[0]).toUpperCase()
                : '?';
            
            // Get user's time balance and format it properly
            const timeBalance = userData.time_balance || 0;
            const balanceText = timeBalance % 1 === 0 ? Math.round(timeBalance) : timeBalance.toFixed(1);
            
            navButtons.innerHTML = `
                <ul class="nav-links">
                    <li><a href="/services" ${activePage === 'services' ? 'class="active"' : ''}>Find Services</a></li>
                    <li><a href="/applications" ${activePage === 'applications' ? 'class="active"' : ''}>Applications</a></li>
                    <li><a href="/my-services" ${activePage === 'my-services' ? 'class="active"' : ''}>My Services</a></li>
                    <li><a href="/messages" ${activePage === 'messages' ? 'class="active"' : ''}>Messages</a></li>
                    <li><a href="/profile" ${activePage === 'profile' ? 'class="active"' : ''}>Profile</a></li>
                </ul>
                <div class="nav-user">
                    <div class="user-balance">
                        ⏱️ <strong id="nav-balance">${balanceText}</strong> ${timeBalance === 1 ? 'hour' : 'hours'}
                    </div>
                    <div class="user-avatar-wrapper">
                        <div class="user-avatar" id="user-avatar-btn" title="My Account">
                            ${initials}
                        </div>
                        <div class="user-dropdown" id="user-dropdown" style="display: none;">
                            <a href="/profile" class="dropdown-item">
                                <span class="dropdown-icon">👤</span>
                                My Profile
                            </a>
                            <div class="dropdown-divider"></div>
                            <a href="#" class="dropdown-item" onclick="NavBar.signOut(); return false;">
                                <span class="dropdown-icon">🚪</span>
                                Sign Out
                            </a>
                        </div>
                    </div>
                </div>
            `;
        } catch (e) {
            console.error('Error rendering authenticated nav:', e);
            this.renderGuestNav(navButtons);
        }
    },

    /**
     * Render navigation for guest users (not logged in)
     */
    renderGuestNav(navButtons) {
        navButtons.innerHTML = `
            <div style="display: flex; gap: 1rem; align-items: center;">
                <a href="/services" class="btn btn-secondary">Browse Services</a>
                <a href="/signin" class="btn btn-secondary">Sign In</a>
                <a href="/signup" class="btn btn-primary">Sign Up</a>
            </div>
        `;
    },

    /**
     * Setup dropdown menu functionality
     */
    setupDropdown() {
        const avatarBtn = document.getElementById('user-avatar-btn');
        const dropdown = document.getElementById('user-dropdown');
        
        if (!avatarBtn || !dropdown) return;
        
        // Toggle dropdown on avatar click
        avatarBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isVisible = dropdown.style.display === 'block';
            dropdown.style.display = isVisible ? 'none' : 'block';
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!avatarBtn.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    },

    /**
     * Handle sign out
     */
    signOut() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/';
    },

    /**
     * Update the time balance display
     * @param {number} balance - The new time balance
     */
    updateBalance(balance) {
        const balanceElement = document.getElementById('nav-balance');
        if (balanceElement) {
            // Format balance to remove .00 from whole numbers
            const balanceText = balance % 1 === 0 ? Math.round(balance) : balance.toFixed(1);
            balanceElement.textContent = balanceText;
            
            // Update the hour/hours text and the entire balance display
            const userBalance = balanceElement.closest('.user-balance');
            if (userBalance) {
                userBalance.innerHTML = `⏱️ <strong id="nav-balance">${balanceText}</strong> ${balance === 1 ? 'hour' : 'hours'}`;
            }
            
            // Also update localStorage to keep it in sync
            const userData = JSON.parse(localStorage.getItem('user') || '{}');
            userData.time_balance = balance;
            localStorage.setItem('user', JSON.stringify(userData));
        }
    }
};

// Make it globally available
window.NavBar = NavBar;
