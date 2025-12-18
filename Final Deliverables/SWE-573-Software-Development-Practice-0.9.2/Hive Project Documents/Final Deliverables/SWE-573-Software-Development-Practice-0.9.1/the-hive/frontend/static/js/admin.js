/**
 * Admin Panel JavaScript
 * Handles data loading and interactions for admin pages
 */

// Check admin authentication
function checkAdminAuth() {
    const token = localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token || user.role !== 'admin') {
        alert('Access denied. Admin privileges required.');
        window.location.href = '/';
        return false;
    }
    return true;
}

// Load admin stats for dashboard
async function loadAdminStats() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/admin/stats', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load stats');
        
        const data = await response.json();
        
        // Update dashboard stats - only update elements that exist
        const setIfExists = (id, value) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        };
        
        setIfExists('total-users', data.users.total);
        setIfExists('active-users', data.users.active);
        setIfExists('banned-users', data.users.banned);
        setIfExists('warned-users', data.users.warned);
        setIfExists('active-services', data.services.active_services);
        setIfExists('hours-exchanged', data.services.hours_exchanged);
        setIfExists('pending-reports', data.reports.pending);
        setIfExists('forum-threads', data.forum.threads);
        setIfExists('forum-comments', data.forum.comments);
        
    } catch (error) {
        console.error('Error loading admin stats:', error);
    }
}

// Load users list
async function loadUsers(page = 1, status = '', search = '') {
    try {
        const token = localStorage.getItem('access_token');
        let url = `/api/admin/users?page=${page}&per_page=20`;
        if (status) url += `&status=${status}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load users');
        
        const data = await response.json();
        displayUsers(data.users);
        updatePagination(data.pagination, 'users');
        
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Display users in table
function displayUsers(users) {
    const tbody = document.getElementById('users-table-body');
    if (!tbody) return;
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td><strong>${user.first_name} ${user.last_name}</strong></td>
            <td>${user.email}</td>
            <td><span class="badge badge-${user.user_status === 'active' ? 'active' : user.user_status === 'banned' ? 'suspended' : 'pending'}">${user.user_status.charAt(0).toUpperCase() + user.user_status.slice(1)}</span></td>
            <td>${new Date(user.date_joined).toLocaleDateString()}</td>
            <td>${Math.floor(user.time_balance || 0)} hrs</td>
            <td>${user.service_count || 0} services</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-ghost btn-small" onclick="viewUser(${user.id})">View</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Global state for user modal
let currentUserId = null;
let currentUserStatus = null;

// View user details
window.viewUser = async function(userId) {
    currentUserId = userId;
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/admin/users?user_id=${userId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to fetch user details');
        
        const data = await response.json();
        const user = data.users && data.users.length > 0 ? data.users[0] : null;
        
        if (!user) {
            alert('User not found');
            return;
        }
        
        currentUserStatus = user.user_status;
        
        // Update modal with user data
        document.getElementById('modalUserName').textContent = `${user.first_name} ${user.last_name}`;
        document.getElementById('modalUserEmail').textContent = user.email;
        document.getElementById('modalStatus').innerHTML = `<span class="badge badge-${user.user_status === 'active' ? 'active' : user.user_status === 'banned' ? 'suspended' : 'pending'}">${user.user_status.charAt(0).toUpperCase() + user.user_status.slice(1)}</span>`;
        document.getElementById('modalJoined').textContent = new Date(user.date_joined).toLocaleDateString();
        document.getElementById('modalBalance').textContent = `${Math.floor(user.time_balance || 0)} hours`;
        document.getElementById('modalServices').textContent = `${user.service_count || 0} services`;
        document.getElementById('modalReports').textContent = '0';
        document.getElementById('modalWarnings').textContent = '0';
        
        // Update button text based on user status
        const banBtn = document.getElementById('banUserBtn');
        if (banBtn) {
            if (user.user_status === 'banned') {
                banBtn.textContent = '✅ Unban User';
                banBtn.className = 'btn btn-primary';
            } else {
                banBtn.textContent = '🚫 Ban User';
                banBtn.className = 'btn btn-danger';
            }
        }
        
        // Clear activity list
        const activityList = document.getElementById('modalActivity');
        if (activityList) {
            activityList.innerHTML = '<li class="activity-item"><div>No recent activity available</div></li>';
        }
        
        document.getElementById('userModal').classList.add('active');
        
    } catch (error) {
        console.error('Error fetching user details:', error);
        alert('Failed to load user details');
    }
};

// Warn user
window.warnUser = async function() {
    if (!currentUserId) return;
    
    const reason = prompt('Enter warning reason:');
    if (!reason) return;
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/admin/users/${currentUserId}/action`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ action: 'warn', reason })
        });
        
        if (!response.ok) throw new Error('Failed to warn user');
        
        alert('User warned successfully');
        closeUserModal();
        loadUsers();
        
    } catch (error) {
        console.error('Error warning user:', error);
        alert('Failed to warn user');
    }
};

// Ban/unban user
window.banUser = async function() {
    if (!currentUserId) return;
    
    const action = currentUserStatus === 'banned' ? 'activate' : 'ban';
    const actionText = action === 'ban' ? 'ban' : 'unban';
    const reason = prompt(`Enter reason to ${actionText} this user:`);
    if (!reason) return;
    
    if (!confirm(`Are you sure you want to ${actionText} this user?`)) return;
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/admin/users/${currentUserId}/action`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ action, reason })
        });
        
        if (!response.ok) throw new Error(`Failed to ${actionText} user`);
        
        alert(`User ${actionText}ned successfully`);
        closeUserModal();
        loadUsers();
        
    } catch (error) {
        console.error(`Error ${actionText}ning user:`, error);
        alert(`Failed to ${actionText} user`);
    }
};

// Close user modal
window.closeUserModal = function() {
    const modal = document.getElementById('userModal');
    if (modal) {
        modal.classList.remove('active');
    }
    currentUserId = null;
    currentUserStatus = null;
};

// Also expose state variables
window.currentUserId = null;
window.currentUserStatus = null;

// Handle user action (ban/warn/activate)
async function handleUserAction(userId, action) {
    const reason = prompt(`Enter reason for ${action}:`);
    if (!reason) return;
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/admin/users/${userId}/action`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ action, reason })
        });
        
        if (!response.ok) throw new Error(`Failed to ${action} user`);
        
        alert(`User ${action}ed successfully`);
        loadUsers(); // Reload the list
        
    } catch (error) {
        console.error(`Error ${action}ing user:`, error);
        alert(`Failed to ${action} user`);
    }
}

// Load services list
async function loadServices(page = 1, type = '', status = '', search = '') {
    try {
        const token = localStorage.getItem('access_token');
        let url = `/api/admin/services?page=${page}&per_page=20`;
        if (type) url += `&type=${type}`;
        if (status) url += `&status=${status}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load services');
        
        const data = await response.json();
        displayServices(data.services);
        updatePagination(data.pagination, 'services');
        
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

// Display services in table
function displayServices(services) {
    const tbody = document.getElementById('services-table-body');
    if (!tbody) return;
    
    tbody.innerHTML = services.map(service => {
        const statusBadge = service.status === 'open' ? 'badge-open' : 
                           service.status === 'in_progress' ? 'badge-pending' : 
                           service.status === 'completed' ? 'badge-resolved' : 'badge-urgent';
        
        return `
            <tr>
                <td>
                    <div class="service-title">${service.title}</div>
                    <div class="service-meta">🏷️ ${service.tags || 'No tags'} • ${service.hours_required} hours</div>
                </td>
                <td><span class="badge badge-${service.service_type === 'offer' ? 'offer' : 'need'}">${service.service_type.charAt(0).toUpperCase() + service.service_type.slice(1)}</span></td>
                <td>${service.first_name} ${service.last_name.charAt(0)}.</td>
                <td><span class="badge ${statusBadge}">${service.status.charAt(0).toUpperCase() + service.status.slice(1).replace('_', ' ')}</span></td>
                <td>${new Date(service.created_at).toLocaleDateString()}</td>
                <td>${service.application_count} applicants</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-ghost btn-small" 
                                onclick="viewServiceDetail(${service.id}, ${service.user_id}, '${service.title.replace(/'/g, "\\'")}', '${service.tags || 'No tags'}', ${service.hours_required}, '${service.service_type}', '${service.first_name}', '${service.last_name}', '${service.status}', '${service.created_at}', '${(service.description || '').replace(/'/g, "\\'")}')">
                            View
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// View service detail in modal
function viewServiceDetail(serviceId, userId, title, tags, hours, type, firstName, lastName, status, createdAt, description) {
    // Populate modal with service data
    const modal = document.getElementById('serviceModal');
    modal.dataset.serviceId = serviceId;
    modal.dataset.ownerId = userId;
    
    document.getElementById('modalServiceTitle').textContent = title;
    document.getElementById('modalServiceMeta').textContent = `🏷️ ${tags} • ${hours} hours`;
    document.getElementById('modalType').textContent = type.charAt(0).toUpperCase() + type.slice(1);
    document.getElementById('modalOwner').textContent = `${firstName} ${lastName}`;
    document.getElementById('modalStatus').textContent = status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
    document.getElementById('modalDate').textContent = new Date(createdAt).toLocaleDateString();
    document.getElementById('modalHours').textContent = `${hours} hours`;
    document.getElementById('modalLocation').textContent = 'Not specified';
    document.getElementById('modalDescription').textContent = description || 'No description provided';
    
    // Show modal
    modal.classList.add('active');
}

// Warn service owner
async function warnServiceOwner() {
    const modal = document.getElementById('serviceModal');
    const serviceId = modal.dataset.serviceId;
    
    const message = prompt('Enter warning message for the service owner:');
    if (!message) return;
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/admin/services/${serviceId}/warn`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) throw new Error('Failed to send warning');
        
        alert('Warning sent successfully to service owner');
        closeServiceModal();
        
    } catch (error) {
        console.error('Error sending warning:', error);
        alert('Failed to send warning');
    }
}

// Remove service
async function removeService() {
    const modal = document.getElementById('serviceModal');
    const serviceId = modal.dataset.serviceId;
    
    const reason = prompt('Enter reason for removing this service:');
    if (!reason) return;
    
    if (!confirm('Are you sure you want to remove this service? This action cannot be undone.')) return;
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/admin/services/${serviceId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ reason })
        });
        
        if (!response.ok) throw new Error('Failed to remove service');
        
        alert('Service removed successfully');
        closeServiceModal();
        loadServices(); // Reload the list
        
    } catch (error) {
        console.error('Error removing service:', error);
        alert('Failed to remove service');
    }
}

// Close modal
function closeServiceModal() {
    document.getElementById('serviceModal')?.classList.remove('active');
}

function closeUserModal() {
    document.getElementById('userModal')?.classList.remove('active');
}

// Load reports
async function loadReports(page = 1, status = 'open') {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/admin/reports?page=${page}&per_page=20&status=${status}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load reports');
        
        const data = await response.json();
        displayReports(data.reports);
        updatePagination(data.pagination, 'reports');
        
    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

// Load recent reports for dashboard
async function loadRecentReports(limit = 5) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/admin/reports?page=1&per_page=${limit}&status=open`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load recent reports');
        
        const data = await response.json();
        displayRecentReports(data.reports);
        
    } catch (error) {
        console.error('Error loading recent reports:', error);
    }
}

// Display recent reports in dashboard
function displayRecentReports(reports) {
    // Find table in Recent Reports section
    const recentReportsSection = Array.from(document.querySelectorAll('.section-title'))
        .find(title => title.textContent.includes('Recent Reports'));
    if (!recentReportsSection) return;
    
    const tbody = recentReportsSection.closest('.content-section').querySelector('table tbody');
    if (!tbody) return;
    
    tbody.innerHTML = reports.map(report => `
        <tr>
            <td>#R${report.id}</td>
            <td>${report.content_type}</td>
            <td>${report.reporter_first_name} ${report.reporter_last_name.charAt(0)}.</td>
            <td>${report.description || report.reason}</td>
            <td><span class="badge badge-${report.status === 'open' ? 'urgent' : 'resolved'}">${report.status === 'open' ? 'Pending' : 'Resolved'}</span></td>
            <td>${new Date(report.created_at).toLocaleDateString()}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-small" onclick="window.location.href='/admin-reports'">Review</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Load recent users for dashboard
async function loadRecentUsers(limit = 5) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/admin/users?page=1&per_page=${limit}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load recent users');
        
        const data = await response.json();
        displayRecentUsers(data.users);
        
    } catch (error) {
        console.error('Error loading recent users:', error);
    }
}

// Display recent users in dashboard
function displayRecentUsers(users) {
    // Find table in Recently Joined Users section
    const recentUsersSection = Array.from(document.querySelectorAll('.section-title'))
        .find(title => title.textContent.includes('Recently Joined'));
    if (!recentUsersSection) return;
    
    const tbody = recentUsersSection.closest('.content-section').querySelector('table tbody');
    if (!tbody) return;
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td><strong>${user.first_name} ${user.last_name}</strong></td>
            <td>${user.email}</td>
            <td><span class="badge badge-${user.user_status === 'active' ? 'active' : user.user_status === 'banned' ? 'suspended' : 'pending'}">${user.user_status.charAt(0).toUpperCase() + user.user_status.slice(1)}</span></td>
            <td>${new Date(user.date_joined).toLocaleDateString()}</td>
            <td>${Math.floor(user.time_balance || 0)} hrs</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-ghost btn-small" onclick="window.location.href='/admin-users'">View</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Display reports in table
function displayReports(reports) {
    const tbody = document.getElementById('reports-table-body');
    if (!tbody) return;
    
    tbody.innerHTML = reports.map(report => `
        <tr>
            <td>#${report.id}</td>
            <td>
                <strong>${report.content_type}</strong> #${report.content_id}<br>
                <small>${report.reason}</small>
            </td>
            <td>
                ${report.reporter_first_name} ${report.reporter_last_name}<br>
                <small>${report.reporter_email}</small>
            </td>
            <td>
                ${report.reported_first_name || 'N/A'} ${report.reported_last_name || ''}<br>
                <small>${report.reported_user_email || ''}</small>
            </td>
            <td>${new Date(report.created_at).toLocaleDateString()}</td>
            <td><span class="badge badge-${report.status === 'open' ? 'pending' : 'resolved'}">${report.status}</span></td>
            <td>
                ${report.status === 'open' ? `
                    <div class="action-buttons">
                        <button class="btn btn-small btn-primary" onclick="resolveReport(${report.id}, 'resolved')">Resolve</button>
                        <button class="btn btn-small btn-secondary" onclick="resolveReport(${report.id}, 'dismissed')">Dismiss</button>
                    </div>
                ` : `<small>${new Date(report.resolved_at).toLocaleDateString()}</small>`}
            </td>
        </tr>
    `).join('');
}

// Resolve report
async function resolveReport(reportId, action) {
    const notes = prompt(`Enter notes for ${action}:`);
    if (notes === null) return;
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/admin/reports/${reportId}/resolve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ action, notes })
        });
        
        if (!response.ok) throw new Error(`Failed to ${action} report`);
        
        alert(`Report ${action} successfully`);
        loadReports(); // Reload the list
        
    } catch (error) {
        console.error(`Error ${action}ing report:`, error);
        alert(`Failed to ${action} report`);
    }
}

// Update pagination controls
function updatePagination(pagination, type) {
    const container = document.getElementById(`${type}-pagination`);
    if (!container) return;
    
    const { page, pages, total } = pagination;
    
    container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem;">
            <span style="color: var(--text-light); font-size: 0.875rem;">
                Showing page ${page} of ${pages} (${total} total)
            </span>
            <div style="display: flex; gap: 0.5rem;">
                <button class="btn btn-small btn-secondary" ${page === 1 ? 'disabled' : ''} 
                        onclick="load${type.charAt(0).toUpperCase() + type.slice(1)}(${page - 1})">
                    Previous
                </button>
                <button class="btn btn-small btn-secondary" ${page === pages ? 'disabled' : ''} 
                        onclick="load${type.charAt(0).toUpperCase() + type.slice(1)}(${page + 1})">
                    Next
                </button>
            </div>
        </div>
    `;
}

// Update admin header with current user
function updateAdminHeader() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const headerText = document.querySelector('.admin-header p');
    if (headerText && user.first_name) {
        headerText.innerHTML = `Welcome back, <strong>${user.first_name} ${user.last_name}</strong>! As a community administrator, you help maintain a safe and fair environment. Here's what's happening in your community today.`;
    }
}

// Initialize admin page
document.addEventListener('DOMContentLoaded', function() {
    if (!checkAdminAuth()) return;
    
    updateAdminHeader();
    
    // Load data based on current page
    const path = window.location.pathname;
    
    if (path.includes('admin-dashboard')) {
        loadAdminStats();
        loadRecentReports();
        loadRecentUsers();
    } else if (path.includes('admin-users')) {
        loadUsers();
    } else if (path.includes('admin-services')) {
        loadServices();
    } else if (path.includes('admin-reports')) {
        loadReports();
    }
});

// Export functions for global access
window.loadUsers = loadUsers;
window.loadServices = loadServices;
window.viewServiceDetail = viewServiceDetail;
window.warnServiceOwner = warnServiceOwner;
window.removeService = removeService;
window.closeServiceModal = closeServiceModal;
window.closeUserModal = closeUserModal;
window.handleUserAction = handleUserAction;
window.loadReports = loadReports;
window.resolveReport = resolveReport;

