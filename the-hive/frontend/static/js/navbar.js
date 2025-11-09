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
            
            // Get user's time balance (you can fetch from API if needed)
            const timeBalance = userData.time_balance;
            
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
                        ⏱️ <strong id="nav-balance">${timeBalance}</strong> hour${timeBalance !== 1 ? 's' : ''}
                    </div>
                    <div class="user-avatar" onclick="window.location.href='/profile'" title="Go to Profile">
                        ${initials}
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
            balanceElement.textContent = balance;
            // Update the hour/hours text
            const userBalance = balanceElement.closest('.user-balance');
            if (userBalance) {
                userBalance.innerHTML = `⏱️ <strong id="nav-balance">${balance}</strong> hour${balance !== 1 ? 's' : ''}`;
            }
        }
    }
};

// Make it globally available
window.NavBar = NavBar;
