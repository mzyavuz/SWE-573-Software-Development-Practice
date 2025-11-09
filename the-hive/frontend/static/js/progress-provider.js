// Progress tracking for Provider (offering service or responding to need)
const APPLICATION_ID = new URLSearchParams(window.location.search).get('application_id');
let currentProgress = null;
let currentApplication = null;
let currentService = null;
let otherUser = null;

/**
 * Update user's time balance in localStorage and navbar
 * Call this after successful transactions
 */
async function updateUserBalance() {
    try {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        // Fetch current user data to get updated balance
        const response = await fetch('/api/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const data = await response.json();
            const userData = JSON.parse(localStorage.getItem('user') || '{}');
            userData.time_balance = data.user.time_balance;
            localStorage.setItem('user', JSON.stringify(userData));

            // Update navbar if NavBar is available
            if (window.NavBar && window.NavBar.updateBalance) {
                window.NavBar.updateBalance(data.user.time_balance);
            }

            // Update balance indicator on current page
            renderBalanceIndicator();
        }
    } catch (error) {
        console.error('Error updating user balance:', error);
    }
}

async function loadProgressData() {
    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = '/signin';
            return;
        }

        // Get progress data
        const progressResponse = await fetch(`/api/applications/${APPLICATION_ID}/progress`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!progressResponse.ok) {
            throw new Error('Failed to load progress');
        }

        const progressData = await progressResponse.json();
        currentProgress = progressData.progress;
        currentApplication = progressData.application;
        currentService = progressData.service;
        otherUser = progressData.other_user;

        renderProgressStepper();
        renderStatusAlert();
        renderBalanceIndicator();
        renderConsumerInfo();
        renderSidebarInfo();
        renderActionButtons();
        renderServiceDetails();
        loadMessages();

    } catch (error) {
        console.error('Error loading progress:', error);
        document.getElementById('statusAlert').innerHTML = 
            '<strong>Error</strong><p style="margin-top: 0.5rem; font-size: 0.875rem;">Failed to load progress data.</p>';
    }
}

function renderProgressStepper() {
    const stepper = document.getElementById('progressStepper');
    if (!currentProgress) {
        stepper.innerHTML = '<p style="color: var(--text-light);">Loading progress...</p>';
        return;
    }
    
    const steps = [
        { id: 'selected', label: 'Selected', number: 1, date: currentProgress.selected_at },
        { id: 'scheduled', label: 'Scheduled', number: 2, date: currentProgress.scheduled_at },
        { id: 'in_progress', label: 'In Progress', number: 3, date: currentProgress.started_at },
        { id: 'awaiting_confirmation', label: 'Confirmation', number: 4, date: null },
        { id: 'completed', label: 'Completed', number: 5, date: currentProgress.completed_at }
    ];

    const statusOrder = ['selected', 'scheduled', 'in_progress', 'awaiting_confirmation', 'completed'];
    const currentIndex = statusOrder.indexOf(currentProgress.status);

    stepper.innerHTML = steps.map((step, index) => {
        let className = 'stepper-item';
        let circleContent = step.number;
        
        if (index < currentIndex) {
            className += ' completed';
            circleContent = '✓';
        } else if (index === currentIndex) {
            className += ' active';
        }

        const dateStr = step.date ? new Date(step.date).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
        }) : '';

        return `
            <div class="${className}">
                <div class="stepper-circle">${circleContent}</div>
                <div class="stepper-label">${step.label}</div>
                ${dateStr ? `<div class="stepper-date">${dateStr}</div>` : ''}
            </div>
        `;
    }).join('');
}

function renderStatusAlert() {
    const alert = document.getElementById('statusAlert');
    if (!currentProgress) {
        alert.innerHTML = '<p style="color: var(--text-light);">Loading status...</p>';
        return;
    }
    
    // Determine current user's role
    const currentUserId = JSON.parse(atob(localStorage.getItem('access_token').split('.')[1])).user_id;
    const isProvider = currentProgress.provider_id === currentUserId;
    const isConsumer = currentProgress.consumer_id === currentUserId;
    
    // Determine service type
    const serviceType = currentService ? (currentService.service_type || currentService.type) : null;
    const isOffer = serviceType === 'offer';
    
    const statusMessages = {
        'selected': {
            class: 'success',
            title: isOffer 
                ? (isProvider ? '✅ Application Accepted!' : '🎉 You\'ve Been Selected!')
                : (isProvider ? '🎉 You\'ve Been Selected!' : '✅ Request Accepted!'),
            text: isOffer
                ? (isProvider 
                    ? 'You have accepted an application for your offer. Please coordinate the details with the applicant.'
                    : 'Congratulations! Your application has been accepted. Please coordinate the details with the offer provider.')
                : (isProvider
                    ? 'Congratulations! You have been selected for this service. Please coordinate the details with the requester.'
                    : 'You have accepted a request for your service. Please coordinate the details with the requester.')
        },
        'scheduled': {
            class: 'info',
            title: '⏰ Service Scheduled',
            text: `Service scheduled for ${formatDate(currentProgress.scheduled_date)} at ${formatTime(currentProgress.scheduled_time)}. Mark as "In Progress" when you start.`
        },
        'in_progress': {
            class: 'info',
            title: '🔧 Service In Progress',
            text: 'Complete the service and mark it as done when finished.'
        },
        'awaiting_confirmation': {
            class: 'info',
            title: isProvider ? '⏰ Awaiting Requester Confirmation' : '⏰ Awaiting Your Confirmation',
            text: isProvider
                ? 'You\'ve marked the service as complete. Waiting for the service requester to confirm completion.'
                : 'The provider has marked the service as complete. Please confirm if you\'re satisfied with the service.'
        },
        'completed': {
            class: 'success',
            title: '✅ Service Completed!',
            text: `Great work! ${currentProgress.hours} hours have been credited to your account.`
        },
        'cancelled': {
            class: 'error',
            title: '❌ Service Cancelled',
            text: 'This service progress has been cancelled. The schedule proposal was rejected and the service is now available for others.'
        }
    };

    const msg = statusMessages[currentProgress.status];
    if (!msg) {
        alert.className = 'alert-box warning';
        alert.innerHTML = `<strong>⚠️ Unknown Status</strong><p style="margin-top: 0.5rem; font-size: 0.875rem;">Status: ${currentProgress.status}</p>`;
        return;
    }
    alert.className = `alert-box ${msg.class}`;
    alert.innerHTML = `<strong>${msg.title}</strong><p style="margin-top: 0.5rem; font-size: 0.875rem;">${msg.text}</p>`;
}

function renderBalanceIndicator() {
    const indicator = document.getElementById('balanceIndicator');
    if (!currentProgress) {
        indicator.style.display = 'none';
        return;
    }

    // Get current user data
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const currentBalance = parseFloat(userData.time_balance) || 1.0;
    const hours = parseFloat(currentProgress.hours) || 0;
    const maxBalance = 10.0;

    // Determine user role
    const currentUserId = JSON.parse(atob(localStorage.getItem('access_token').split('.')[1])).user_id;
    const isProvider = currentProgress.provider_id === currentUserId;
    const isConsumer = currentProgress.consumer_id === currentUserId;

    // Only show indicator for active statuses (not completed or cancelled)
    if (currentProgress.status === 'completed' || currentProgress.status === 'cancelled') {
        indicator.style.display = 'none';
        return;
    }

    // Calculate balance impact
    let balanceClass = 'balance-indicator';
    let icon = '⏱️';
    let title = 'Your Time Balance';
    let message = '';
    let impact = '';
    let afterBalance = 0;
    
    if (isConsumer) {
        afterBalance = currentBalance - hours;
        
        if (currentBalance < hours) {
            // Insufficient balance - critical
            balanceClass += ' danger';
            icon = '⚠️';
            title = 'Insufficient Time Balance';
            message = `You have ${currentBalance.toFixed(1)} hours, but this service requires ${hours} hours.`;
            impact = `<div class="balance-impact">
                <span style="color: #ef4444;">❌ Short by ${(hours - currentBalance).toFixed(1)} hours</span>
            </div>`;
        } else if (afterBalance < 1.0) {
            // Low balance after service - warning
            balanceClass += ' warning';
            icon = '⚠️';
            title = 'Low Time Balance After Service';
            message = `Current: ${currentBalance.toFixed(1)} hours | Service requires: ${hours} hours`;
            impact = `<div class="balance-impact">
                <span style="color: #f59e0b;">After service: ${afterBalance.toFixed(1)} hours remaining</span>
            </div>`;
        } else {
            // Sufficient balance - normal
            message = `Current: ${currentBalance.toFixed(1)} hours | Service requires: ${hours} hours`;
            impact = `<div class="balance-impact">
                <span style="color: #10b981;">After service: ${afterBalance.toFixed(1)} hours remaining</span>
            </div>`;
        }
    } else if (isProvider) {
        afterBalance = currentBalance + hours;
        
        if (afterBalance > maxBalance) {
            // Would exceed maximum - critical
            balanceClass += ' danger';
            icon = '⚠️';
            title = 'Would Exceed Maximum Balance';
            message = `You have ${currentBalance.toFixed(1)} hours. This service provides ${hours} hours.`;
            impact = `<div class="balance-impact">
                <span style="color: #ef4444;">❌ Would reach ${afterBalance.toFixed(1)} hours (Max: ${maxBalance} hours)</span>
            </div>`;
        } else if (afterBalance >= 8.0) {
            // Close to maximum - warning
            balanceClass += ' warning';
            icon = '⚠️';
            title = 'Approaching Maximum Balance';
            message = `Current: ${currentBalance.toFixed(1)} hours | Service provides: ${hours} hours`;
            impact = `<div class="balance-impact">
                <span style="color: #f59e0b;">After service: ${afterBalance.toFixed(1)} hours (${(maxBalance - afterBalance).toFixed(1)} hours until max)</span>
            </div>`;
        } else {
            // Normal - will earn hours
            message = `Current: ${currentBalance.toFixed(1)} hours | Service provides: ${hours} hours`;
            impact = `<div class="balance-impact">
                <span style="color: #10b981;">After service: ${afterBalance.toFixed(1)} hours</span>
            </div>`;
        }
    }

    indicator.className = balanceClass;
    indicator.style.display = 'flex';
    indicator.innerHTML = `
        <div class="balance-icon">${icon}</div>
        <div class="balance-content">
            <div class="balance-title">${title}</div>
            <div class="balance-text">${message}</div>
            ${impact}
        </div>
    `;
}

function renderConsumerInfo() {
    const container = document.getElementById('consumerInfo');
    if (!otherUser) {
        container.innerHTML = '<p style="color: var(--text-light);">Loading user info...</p>';
        return;
    }
    
    const initials = otherUser.full_name ? 
        otherUser.full_name.split(' ').map(n => n[0]).join('').toUpperCase() : 
        (otherUser.email ? otherUser.email[0].toUpperCase() : '?');
    
    // Determine the label based on service type
    const serviceType = currentService ? (currentService.service_type || currentService.type) : null;

    container.innerHTML = `
        <div class="consumer-header">
            <div class="consumer-avatar">${initials}</div>
            <div class="consumer-details">
                <div class="consumer-name">${otherUser.full_name || otherUser.email || 'Unknown'}</div>
            </div>
            <button class="btn btn-ghost" onclick="window.location.href='/user/${otherUser.id}'">View Profile</button>
        </div>
    `;
}

function renderSidebarInfo() {
    document.getElementById('sidebarStatus').textContent = formatStatus(currentProgress.status);
    document.getElementById('appliedDate').textContent = formatDate(currentApplication.applied_at);
    const hoursNum = parseFloat(currentProgress.hours);
    const hoursText = Number.isFinite(hoursNum) ? hoursNum.toString() : String(currentProgress.hours);
    document.getElementById('estimatedHours').textContent = `${hoursText} hrs`;
        
    // Show the service location (needs should have a location)
    const location = currentProgress.agreed_location || 
                    (currentService && currentService.location) || 
                    'Not specified';
    document.getElementById('locationDistance').textContent = location;

    if (currentProgress.scheduled_date) {
        document.getElementById('scheduledDateRow').style.display = 'flex';
        document.getElementById('scheduledDate').textContent = formatDate(currentProgress.scheduled_date);
    }

    if (currentProgress.scheduled_time) {
        document.getElementById('scheduledTimeRow').style.display = 'flex';
        document.getElementById('scheduledTime').textContent = formatTime(currentProgress.scheduled_time);
    }
}

function renderActionButtons() {
    const container = document.getElementById('actionButtons');
    let buttons = '';

    // If service is cancelled, show no action buttons
    if (currentProgress.status === 'cancelled') {
        buttons = `
            <p style="font-size: 0.875rem; color: var(--text-light); text-align: center; padding: 1rem;">
                This service has been cancelled. No actions are available.
            </p>
        `;
        container.innerHTML = buttons;
        
        // Also disable message input
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.querySelector('.message-input button');
        if (messageInput) {
            messageInput.disabled = true;
            messageInput.placeholder = 'Service cancelled - messaging disabled';
        }
        if (sendButton) {
            sendButton.disabled = true;
        }
        return;
    }

    switch(currentProgress.status) {
        case 'selected':
            buttons = `
                <button class="btn btn-primary" style="width:100%; margin-bottom:0.5rem;" onclick="openScheduleProposal()">
                    📅 Propose Schedule
                </button>
                <p style="font-size: 0.875rem; color: var(--text-light); margin-top: 0.5rem;">
                    Propose a date and time for this service.
                </p>
            `;
            break;
        case 'scheduled':
            // Check start confirmation status
            const providerStartConfirmed = currentProgress.provider_start_confirmed || false;
            const consumerStartConfirmed = currentProgress.consumer_start_confirmed || false;
            const isProvider = currentProgress.is_provider || false;
            
            if (!providerStartConfirmed && !consumerStartConfirmed) {
                // Neither party confirmed
                buttons = `
                    <button class="btn btn-primary" style="width:100%; margin-bottom:0.5rem;" onclick="confirmStart()">
                        ✅ Confirm Service Started
                    </button>
                    <button class="btn btn-secondary" style="width:100%; margin-bottom:0.5rem;" onclick="openScheduleProposal()">
                        📅 Change Schedule
                    </button>
                    <button class="btn btn-ghost" style="width:100%;" onclick="reportIssue()">
                        ⚠️ Report Issue
                    </button>
                `;
            } else if ((isProvider && providerStartConfirmed) || (!isProvider && consumerStartConfirmed)) {
                // Current user confirmed, waiting for other party
                buttons = `
                    <div class="alert alert-info" style="margin-bottom: 1rem;">
                        <strong>✅ You confirmed service started</strong><br>
                        <span style="font-size: 0.875rem;">⏳ Waiting for ${isProvider ? 'consumer' : 'provider'} to confirm...</span>
                    </div>
                    <button class="btn btn-secondary" style="width:100%; margin-bottom:0.5rem;" onclick="openScheduleProposal()">
                        📅 Change Schedule
                    </button>
                    <button class="btn btn-ghost" style="width:100%;" onclick="reportIssue()">
                        ⚠️ Report Issue
                    </button>
                `;
            } else {
                // Other party confirmed, current user hasn't
                buttons = `
                    <div class="alert alert-warning" style="margin-bottom: 1rem;">
                        <strong>⏳ ${isProvider ? 'Consumer' : 'Provider'} confirmed service started</strong><br>
                        <span style="font-size: 0.875rem;">Please confirm to start the service</span>
                    </div>
                    <button class="btn btn-primary" style="width:100%; margin-bottom:0.5rem;" onclick="confirmStart()">
                        ✅ Confirm Service Started
                    </button>
                    <button class="btn btn-secondary" style="width:100%; margin-bottom:0.5rem;" onclick="openScheduleProposal()">
                        📅 Change Schedule
                    </button>
                    <button class="btn btn-ghost" style="width:100%;" onclick="reportIssue()">
                        ⚠️ Report Issue
                    </button>
                `;
            }
            break;
        case 'in_progress':
            buttons = `
                <button class="btn btn-primary" style="width:100%; margin-bottom:0.5rem;" onclick="markComplete()">
                    ✅ Mark as Complete
                </button>
                <button class="btn btn-secondary" style="width:100%; margin-bottom:0.5rem;" onclick="openScheduleProposal()">
                    📅 Reschedule
                </button>
                <button class="btn btn-ghost" style="width:100%;" onclick="reportIssue()">
                    ⚠️ Report Issue
                </button>
            `;
            break;
        case 'awaiting_confirmation':
            // Check if current user has already submitted survey
            const userIsProvider = currentProgress.is_provider;
            const userSubmitted = userIsProvider 
                ? currentProgress.provider_survey_submitted 
                : currentProgress.consumer_survey_submitted;
            
            if (userSubmitted) {
                buttons = `
                    <div class="alert alert-info" style="margin-bottom: 1rem;">
                        <strong>✅ You've submitted your confirmation</strong><br>
                        <span style="font-size: 0.875rem;">⏳ Waiting for the other party...</span>
                    </div>
                    <button class="btn btn-ghost" style="width:100%;" onclick="reportIssue()">
                        ⚠️ Report Issue
                    </button>
                `;
            } else {
                buttons = `
                    <div class="alert alert-warning" style="margin-bottom: 1rem;">
                        <strong>📋 Confirmation Required</strong><br>
                        <span style="font-size: 0.875rem;">Please complete the confirmation form</span>
                    </div>
                    <button class="btn btn-primary" style="width:100%; margin-bottom:0.5rem;" onclick="submitSurvey()">
                        ✅ Complete Confirmation
                    </button>
                    <button class="btn btn-ghost" style="width:100%;" onclick="reportIssue()">
                        ⚠️ Report Issue
                    </button>
                `;
            }
            break;
        case 'completed':
            buttons = `
                <button class="btn btn-primary" style="width:100%; margin-bottom:0.5rem;" onclick="leaveReview()">
                    ⭐ Leave Review
                </button>
            `;
            break;
    }

    container.innerHTML = buttons;
}

function renderServiceDetails() {
    const container = document.getElementById('serviceDetailsCard');
    const statusBadge = `<span class="status-badge status-${currentProgress.status}">${formatStatus(currentProgress.status)}</span>`;

    // Determine service type
    const serviceType = currentService.service_type || currentService.type;

    // Build need details section if this is a need service
    let needDetailsHtml = '';
    if (serviceType === 'need') {
        const details = [];
        
        if (currentService.location_address) {
            details.push(`<strong>📍 Location:</strong> ${currentService.location_address}`);
        }
        
        if (currentService.service_date) {
            details.push(`<strong>📅 Date:</strong> ${formatDate(currentService.service_date)}`);
        }
        
        if (currentService.start_time && currentService.end_time) {
            // only hh:mm - hh:mm
            const start = currentService.start_time ? currentService.start_time.split(':').slice(0,2).join(':') : '';
            const end = currentService.end_time ? currentService.end_time.split(':').slice(0,2).join(':') : '';
            details.push(`<strong>🕐 Time:</strong> ${start} - ${end}`);
        } else if (currentService.start_time) {
            const start = currentService.start_time.split(':').slice(0,2).join(':');
            details.push(`<strong>🕐 Start Time:</strong> ${start}`);
        } else if (currentService.end_time) {
            const end = currentService.end_time.split(':').slice(0,2).join(':');
            details.push(`<strong>🕐 End Time:</strong> ${end}`);
        }
        
        if (details.length > 0) {
            needDetailsHtml = `
                <div style="background: var(--bg-light); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="font-size: 0.875rem; color: var(--text-dark);">
                        ${details.join('<br>')}
                    </div>
                </div>
            `;
        }
    }

    // Build availability section for offers
    let availabilityHtml = '';
    if (serviceType === 'offer' && currentProgress.availability && currentProgress.availability.length > 0) {
        const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        const availabilityMap = {};
        
        currentProgress.availability.forEach(avail => {
            availabilityMap[avail.day_of_week] = {
                start_time: avail.start_time.substring(0, 5), // HH:MM
                end_time: avail.end_time.substring(0, 5)
            };
        });
        
        const availabilityRows = daysOfWeek.map((day, index) => {
            const dayAvail = availabilityMap[index];
            if (dayAvail) {
                return `
                    <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: #d1fae5; border-radius: 6px; margin-bottom: 0.25rem;">
                        <span style="font-weight: 600; color: #065f46;">${day}</span>
                        <span style="color: #059669;">${dayAvail.start_time} - ${dayAvail.end_time}</span>
                    </div>
                `;
            }
            return '';
        }).filter(row => row).join('');
        
        if (availabilityRows) {
            availabilityHtml = `
                <div style="margin-bottom: 1rem;">
                    <h3 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-dark);">📅 Availability</h3>
                    ${availabilityRows}
                </div>
            `;
        }
    }

    container.innerHTML = `
        <div class="status-header">
            <div>
                <h2 class="service-title" style="font-size: 1.25rem;">${currentService.title}</h2>
                <div class="service-meta">
                    Posted ${formatDate(currentService.created_at)}
                </div>
            </div>
            ${statusBadge}
        </div>
        ${needDetailsHtml}
        ${availabilityHtml}
        ${currentService.description ? `
            <p style="color: var(--text-light); margin-bottom: 1rem;">
                ${currentService.description}
            </p>
        ` : ''}
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            ${currentService.tags ? currentService.tags.split(',').map(tag => 
                `<span class="tag">${tag.trim()}</span>`
            ).join('') : ''}
        </div>
    `;
}

async function loadMessages() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/applications/${APPLICATION_ID}/messages`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const messages = await response.json();
            renderMessages(messages);
            renderProposalNotification(messages);
        }
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

// Check if there's a pending proposal
let hasPendingProposal = false;

function renderProposalNotification(messages) {
    const notificationContainer = document.getElementById('proposalNotification');
    const currentUserId = JSON.parse(atob(localStorage.getItem('access_token').split('.')[1])).user_id;
    
    // Find pending schedule proposal
    const pendingProposal = messages.find(msg => 
        msg.message_type === 'schedule_proposal' && 
        msg.proposal_status === 'pending'
    );
    
    // Update global flag
    hasPendingProposal = !!pendingProposal;
    
    if (!pendingProposal) {
        notificationContainer.style.display = 'none';
        notificationContainer.innerHTML = '';
        return;
    }
    
    const isSender = pendingProposal.sender_id === currentUserId;
    const isReceiver = !isSender;
    
    let notificationHTML = `
        <div class="proposal-notification">
            <h4>📅 Pending Schedule Proposal</h4>
            <div class="proposal-details">
                <div class="proposal-details-row">
                    <span class="proposal-details-label">Date:</span>
                    <span class="proposal-details-value">${formatDate(pendingProposal.proposal_date)}</span>
                </div>
                <div class="proposal-details-row">
                    <span class="proposal-details-label">Time:</span>
                    <span class="proposal-details-value">${formatTime(pendingProposal.proposal_start_time)} - ${formatTime(pendingProposal.proposal_end_time)}</span>
                </div>
                ${pendingProposal.proposal_location ? `
                    <div class="proposal-details-row">
                        <span class="proposal-details-label">Location:</span>
                        <span class="proposal-details-value">${pendingProposal.proposal_location}</span>
                    </div>
                ` : ''}
                <div class="proposal-details-row">
                    <span class="proposal-details-label">Proposed by:</span>
                    <span class="proposal-details-value">${isSender ? 'You' : pendingProposal.sender_first_name + ' ' + pendingProposal.sender_last_name}</span>
                </div>
            </div>
            
            ${isReceiver ? `
                <div class="proposal-actions">
                    <button class="btn-reject-proposal" onclick="respondToScheduleProposal(${pendingProposal.id}, false)">
                        ✗ Reject Proposal
                    </button>
                    <button class="btn-accept-proposal" onclick="respondToScheduleProposal(${pendingProposal.id}, true)">
                        ✓ Accept Proposal
                    </button>
                </div>
            ` : `
                <div class="proposal-actions">
                    <button class="btn-cancel-proposal" onclick="cancelScheduleProposal(${pendingProposal.id})">
                        🗑️ Cancel Proposal
                    </button>
                </div>
                <div class="proposal-warning">
                    <span>⚠️</span>
                    <span>While a proposal is pending, neither party can submit new proposals. You can cancel this proposal if you wish to make changes.</span>
                </div>
            `}
        </div>
    `;
    
    notificationContainer.innerHTML = notificationHTML;
    notificationContainer.style.display = 'block';
}


function renderMessages(messages) {
    const thread = document.getElementById('messageThread');
    const currentUserId = JSON.parse(atob(localStorage.getItem('access_token').split('.')[1])).user_id;

    thread.innerHTML = messages.map(msg => {
        const isCurrentUser = msg.sender_id === currentUserId;
        const messageClass = isCurrentUser ? 'message current-user' : 'message other-user';

        // Check if this is a schedule proposal message
        if (msg.message_type === 'schedule_proposal') {
            const isPending = msg.proposal_status === 'pending';
            const isReceiver = msg.receiver_id === currentUserId;
            
            let statusBadge = '';
            let actionButtons = '';
            
            if (msg.proposal_status === 'accepted') {
                statusBadge = '<span class="proposal-status accepted">✓ Accepted</span>';
            } else if (msg.proposal_status === 'rejected') {
                statusBadge = '<span class="proposal-status rejected">✗ Rejected</span>';
            } else if (isPending && isReceiver) {
                // Show action buttons only for receiver with pending status
                actionButtons = `
                    <div class="proposal-actions">
                        <button class="btn-accept" onclick="respondToSchedule(${msg.id}, true)">
                            ✓ Accept
                        </button>
                        <button class="btn-reject" onclick="respondToSchedule(${msg.id}, false)">
                            ✗ Reject
                        </button>
                    </div>
                `;
            } else if (isPending) {
                statusBadge = '<span class="proposal-status pending">⏳ Waiting for response</span>';
            }

            return `
                <div class="${messageClass} schedule-proposal">
                    <div class="message-content">
                        <div class="proposal-header">📅 Schedule Proposal</div>
                        <div class="proposal-details">
                            <div class="proposal-item">
                                <strong>Date:</strong> ${formatDate(msg.proposal_date)}
                            </div>
                            <div class="proposal-item">
                                <strong>Time:</strong> ${formatTime(msg.proposal_start_time)} - ${formatTime(msg.proposal_end_time)}
                            </div>
                            ${msg.proposal_location ? `
                                <div class="proposal-item">
                                    <strong>Location:</strong> ${msg.proposal_location}
                                </div>
                            ` : ''}
                        </div>
                        ${statusBadge}
                        ${actionButtons}
                    </div>
                    <div class="message-time">${formatDateTime(msg.created_at)}</div>
                </div>
            `;
        }

        // Regular text message
        return `
            <div class="${messageClass}">
                <div class="message-content">
                    <div class="message-text">${msg.message}</div>
                </div>
                <div class="message-time">${formatDateTime(msg.created_at)}</div>
            </div>
        `;
    }).join('');

    // Scroll to bottom
    thread.scrollTop = thread.scrollHeight;
}

async function respondToSchedule(messageId, accept) {
    const action = accept ? 'accept' : 'reject';
    
    if (accept) {
        // First, fetch the message to get proposal times and calculate hours
        try {
            const token = localStorage.getItem('access_token');
            const messagesResponse = await fetch(`/api/applications/${APPLICATION_ID}/messages`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (!messagesResponse.ok) {
                throw new Error('Failed to load message data');
            }
            
            const messages = await messagesResponse.json();
            const message = messages.find(m => m.id === messageId);
            
            if (!message || !message.proposal_start_time || !message.proposal_end_time) {
                throw new Error('Invalid message data');
            }
            
            // Calculate hours from proposed schedule
            const startTime = message.proposal_start_time.split(':');
            const endTime = message.proposal_end_time.split(':');
            const startMinutes = parseInt(startTime[0]) * 60 + parseInt(startTime[1]);
            const endMinutes = parseInt(endTime[0]) * 60 + parseInt(endTime[1]);
            const scheduledHours = (endMinutes - startMinutes) / 60;
            
            // Get user balance and role
            const userData = JSON.parse(localStorage.getItem('user'));
            const currentBalance = parseFloat(userData.time_balance) || 1.0;
            const maxBalance = 10.0;
            const isProvider = currentProgress.is_provider;
            const isConsumer = !isProvider;
            
            // Build warning message
            let confirmMessage = `Accept this proposed schedule?\n\n`;
            confirmMessage += `📅 Proposed Schedule: ${message.proposal_date}\n`;
            confirmMessage += `⏰ Time: ${message.proposal_start_time} - ${message.proposal_end_time}\n`;
            confirmMessage += `⏱️ Duration: ${scheduledHours.toFixed(1)} hours\n\n`;
            confirmMessage += `Current Balance: ${currentBalance.toFixed(1)} hours\n`;
            
            if (isConsumer) {
                const afterBalance = currentBalance - scheduledHours;
                confirmMessage += `After Service: ${afterBalance.toFixed(1)} hours\n\n`;
                
                if (currentBalance < scheduledHours) {
                    confirmMessage += `⚠️ WARNING: You have ${currentBalance.toFixed(1)} hours but this service requires ${scheduledHours.toFixed(1)} hours.\n`;
                    confirmMessage += `You need ${(scheduledHours - currentBalance).toFixed(1)} more hours to proceed.\n\n`;
                    confirmMessage += `Do you want to proceed anyway?`;
                } else if (afterBalance < 0.5) {
                    confirmMessage += `⚠️ WARNING: Your balance will be very low (${afterBalance.toFixed(1)} hours) after this service.\n\n`;
                    confirmMessage += `Continue?`;
                } else {
                    confirmMessage += `Continue with this schedule?`;
                }
            } else {
                // Provider
                const afterBalance = currentBalance + scheduledHours;
                confirmMessage += `After Service: ${afterBalance.toFixed(1)} hours\n\n`;
                
                if (afterBalance > maxBalance) {
                    const excess = afterBalance - maxBalance;
                    confirmMessage += `⚠️ WARNING: Accepting this will give you ${afterBalance.toFixed(1)} hours, exceeding the ${maxBalance.toFixed(1)}-hour limit by ${excess.toFixed(1)} hours.\n\n`;
                    confirmMessage += `Do you want to proceed anyway?`;
                } else if (afterBalance >= maxBalance - 1.0) {
                    confirmMessage += `⚠️ WARNING: Your balance will be near the maximum (${afterBalance.toFixed(1)} hours) after this service.\n\n`;
                    confirmMessage += `Continue?`;
                } else {
                    confirmMessage += `Continue with this schedule?`;
                }
            }
            
            if (!confirm(confirmMessage)) return;
            
        } catch (error) {
            console.error('Error calculating schedule hours:', error);
            // Fallback to simple confirmation
            if (!confirm('Accept this proposed schedule? The service will proceed with these new times.')) return;
        }
    } else {
        if (!confirm('Reject this proposed schedule? This will cancel the progress and reopen the service to others.')) return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/messages/${messageId}/respond-schedule`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ accept })
        });

        if (response.ok) {
            const result = await response.json();
            alert(result.message);
            // Reload messages and progress data
            loadMessages();
            loadProgressData();
        } else {
            const error = await response.json();
            alert('❌ Cannot Accept Schedule\n\n' + (error.error || `Failed to ${action} schedule`));
        }
    } catch (error) {
        console.error(`Error ${action}ing schedule:`, error);
        alert(`❌ Failed to ${action} schedule`);
    }
}

// Function to respond to proposal from notification banner
async function respondToScheduleProposal(messageId, accept) {
    const action = accept ? 'accept' : 'reject';
    
    if (accept) {
        // First, fetch the message to get proposal times and calculate hours
        try {
            const token = localStorage.getItem('access_token');
            const messagesResponse = await fetch(`/api/applications/${APPLICATION_ID}/messages`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (!messagesResponse.ok) {
                throw new Error('Failed to load message data');
            }
            
            const messages = await messagesResponse.json();
            const message = messages.find(m => m.id === messageId);
            
            if (!message || !message.proposal_start_time || !message.proposal_end_time) {
                throw new Error('Invalid message data');
            }
            
            // Calculate hours from proposed schedule
            const startTime = message.proposal_start_time.split(':');
            const endTime = message.proposal_end_time.split(':');
            const startMinutes = parseInt(startTime[0]) * 60 + parseInt(startTime[1]);
            const endMinutes = parseInt(endTime[0]) * 60 + parseInt(endTime[1]);
            const scheduledHours = (endMinutes - startMinutes) / 60;
            
            // Get user balance and role
            const userData = JSON.parse(localStorage.getItem('user'));
            const currentBalance = parseFloat(userData.time_balance) || 1.0;
            const maxBalance = 10.0;
            const isProvider = currentProgress.is_provider;
            const isConsumer = !isProvider;
            
            // Build warning message
            let confirmMessage = `Accept this proposed schedule?\n\n`;
            confirmMessage += `📅 Proposed Schedule: ${message.proposal_date}\n`;
            confirmMessage += `⏰ Time: ${message.proposal_start_time} - ${message.proposal_end_time}\n`;
            confirmMessage += `⏱️ Duration: ${scheduledHours.toFixed(1)} hours\n\n`;
            confirmMessage += `Current Balance: ${currentBalance.toFixed(1)} hours\n`;
            
            if (isConsumer) {
                const afterBalance = currentBalance - scheduledHours;
                confirmMessage += `After Service: ${afterBalance.toFixed(1)} hours\n\n`;
                
                if (currentBalance < scheduledHours) {
                    confirmMessage += `⚠️ WARNING: You have ${currentBalance.toFixed(1)} hours but this service requires ${scheduledHours.toFixed(1)} hours.\n`;
                    confirmMessage += `You need ${(scheduledHours - currentBalance).toFixed(1)} more hours to proceed.\n\n`;
                    confirmMessage += `Do you want to proceed anyway?`;
                } else if (afterBalance < 0.5) {
                    confirmMessage += `⚠️ WARNING: Your balance will be very low (${afterBalance.toFixed(1)} hours) after this service.\n\n`;
                    confirmMessage += `Continue?`;
                } else {
                    confirmMessage += `Continue with this schedule?`;
                }
            } else {
                // Provider
                const afterBalance = currentBalance + scheduledHours;
                confirmMessage += `After Service: ${afterBalance.toFixed(1)} hours\n\n`;
                
                if (afterBalance > maxBalance) {
                    const excess = afterBalance - maxBalance;
                    confirmMessage += `⚠️ WARNING: Accepting this will give you ${afterBalance.toFixed(1)} hours, exceeding the ${maxBalance.toFixed(1)}-hour limit by ${excess.toFixed(1)} hours.\n\n`;
                    confirmMessage += `Do you want to proceed anyway?`;
                } else if (afterBalance >= maxBalance - 1.0) {
                    confirmMessage += `⚠️ WARNING: Your balance will be near the maximum (${afterBalance.toFixed(1)} hours) after this service.\n\n`;
                    confirmMessage += `Continue?`;
                } else {
                    confirmMessage += `Continue with this schedule?`;
                }
            }
            
            if (!confirm(confirmMessage)) return;
            
        } catch (error) {
            console.error('Error calculating schedule hours:', error);
            // Fallback to simple confirmation
            if (!confirm('Accept this proposed schedule? The service will be scheduled with these details.')) return;
        }
    } else {
        if (!confirm('Reject this proposed schedule? This will cancel the progress and reopen the service to others.')) return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/messages/${messageId}/respond-schedule`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ accept })
        });

        if (response.ok) {
            const result = await response.json();
            alert(result.message);
            // Reload messages and progress data
            loadMessages();
            loadProgressData();
        } else {
            const error = await response.json();
            alert('❌ Cannot Accept Schedule\n\n' + (error.error || `Failed to ${action} schedule`));
        }
    } catch (error) {
        console.error(`Error ${action}ing schedule:`, error);
        alert(`❌ Failed to ${action} schedule`);
    }
}

// Function to cancel a pending proposal
async function cancelScheduleProposal(messageId) {
    const confirmMessage = 'Are you sure you want to cancel this proposal? You will be able to submit a new one afterward.';
    
    if (!confirm(confirmMessage)) return;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/messages/${messageId}/cancel-proposal`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            alert(result.message);
            // Reload messages to refresh the UI
            loadMessages();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to cancel proposal');
        }
    } catch (error) {
        console.error('Error canceling proposal:', error);
        alert('Failed to cancel proposal');
    }
}


async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Check if service is cancelled
    if (currentProgress.status === 'cancelled') {
        alert('Cannot send messages for a cancelled service');
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/messages`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                message,
                receiver_id: otherUser.id,
                application_id: currentApplication.id,
                service_id: currentService.id
            })
        });

        if (response.ok) {
            input.value = '';
            loadMessages();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to send message');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        alert('Failed to send message');
    }
}

async function confirmStart() {
    let confirmMessage = 'Confirm that the service has started?';
    
    // Add balance warning
    if (currentProgress) {
        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        const currentBalance = parseFloat(userData.time_balance) || 1.0;
        const maxBalance = 10.0;
        const hours = parseFloat(currentProgress.hours) || 0;
        const isProvider = currentProgress.is_provider;
        const isConsumer = !isProvider;
        
        // Warn consumer about insufficient balance
        if (isConsumer && currentBalance < hours) {
            const shortage = hours - currentBalance;
            confirmMessage += `\n\n⚠️ WARNING: You have ${currentBalance.toFixed(1)} hours but this service requires ${hours.toFixed(1)} hours. You need ${shortage.toFixed(1)} more hours. The service cannot start until you have sufficient balance.`;
        }
        
        // Warn provider about exceeding maximum
        if (isProvider && (currentBalance + hours) > maxBalance) {
            const afterBalance = currentBalance + hours;
            const excess = afterBalance - maxBalance;
            confirmMessage += `\n\n⚠️ WARNING: Completing this service will give you ${afterBalance.toFixed(1)} hours, exceeding the ${maxBalance.toFixed(1)}-hour limit by ${excess.toFixed(1)} hours. The service cannot start until this is resolved.`;
        }
        
        // Add balance info for both
        confirmMessage += `\n\nYour current balance: ${currentBalance.toFixed(1)} hours`;
        if (isConsumer) {
            const afterBalance = currentBalance - hours;
            confirmMessage += `\nAfter service: ${afterBalance.toFixed(1)} hours`;
        } else {
            const afterBalance = currentBalance + hours;
            confirmMessage += `\nAfter service: ${afterBalance.toFixed(1)} hours`;
        }
    }
    
    if (!confirm(confirmMessage)) return;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/progress/${currentProgress.id}/confirm-start`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            
            // Update balance if both parties confirmed (transaction happened)
            if (result.both_confirmed) {
                await updateUserBalance();
                alert('✅ Service started! Both parties confirmed.');
            } else {
                alert('✅ Your confirmation recorded. Waiting for the other party to confirm.');
            }
            window.location.reload();
        } else {
            const error = await response.json();
            alert('❌ Cannot Confirm Start\n\n' + (error.error || 'Failed to confirm start'));
        }
    } catch (error) {
        console.error('Error confirming start:', error);
        alert('❌ Failed to confirm start');
    }
}

async function startProgress() {
    if (!confirm('Mark this service as "In Progress"?')) return;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/progress/${currentProgress.id}/status`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: 'in_progress' })
        });

        if (response.ok) {
            window.location.reload();
        } else {
            alert('Failed to update status');
        }
    } catch (error) {
        console.error('Error updating status:', error);
        alert('Failed to update status');
    }
}

async function markComplete() {
    if (!confirm('Mark this service as complete? You will be asked to complete a confirmation form.')) return;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/progress/${currentProgress.id}/mark-finished`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const result = await response.json();
            
            // TODO: Show survey modal here instead of reloading
            // For now, just reload to show the awaiting_confirmation status
            alert(result.message + '\n\nNote: Survey forms are not yet implemented. The service will auto-complete in 24 hours.');
            window.location.reload();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to mark as complete');
        }
    } catch (error) {
        console.error('Error marking complete:', error);
        alert('Failed to mark as complete');
    }
}

async function submitSurvey() {
    // Show survey modal instead of simple confirm
    openSurveyModal();
}

function openSurveyModal() {
    if (!currentProgress) return;
    
    // Format date properly (without time)
    let formattedDate = 'N/A';
    if (currentProgress.scheduled_date) {
        const dateObj = new Date(currentProgress.scheduled_date);
        formattedDate = dateObj.toLocaleDateString('en-US', { 
            weekday: 'short',
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
        });
    }
    
    // Format hours as integer if whole number
    const hours = parseFloat(currentProgress.hours) || 0;
    const hoursDisplay = hours % 1 === 0 ? Math.round(hours) : hours.toFixed(1);
    
    // Populate service summary
    const summaryHtml = `
        <h3>Service Summary</h3>
        <div class="summary-row">
            <span class="summary-label">Service</span>
            <span class="summary-value">${currentService.title}</span>
        </div>
        <div class="summary-row">
            <span class="summary-label">Consumer</span>
            <span class="summary-value">${otherUser.full_name}</span>
        </div>
        <div class="summary-row">
            <span class="summary-label">Date</span>
            <span class="summary-value">${formattedDate}</span>
        </div>
        <div class="summary-row">
            <span class="summary-label">Time</span>
            <span class="summary-value">${currentProgress.scheduled_time || 'N/A'}</span>
        </div>
        <div class="summary-row">
            <span class="summary-label">Estimated Hours</span>
            <span class="summary-value">${hoursDisplay} ${hours === 1 ? 'hour' : 'hours'}</span>
        </div>
        <div class="summary-row highlight">
            <span class="summary-label">Time Credits to Receive</span>
            <span class="summary-value">${hoursDisplay} ${hours === 1 ? 'hour' : 'hours'}</span>
        </div>
    `;
    document.getElementById('surveySummary').innerHTML = summaryHtml;
    
    // Update time estimate text
    document.getElementById('timeEstimateText').textContent = 
        `The task was estimated at ${hoursDisplay} ${hours === 1 ? 'hour' : 'hours'}`;
    
    // Show modal
    document.getElementById('surveyModal').classList.add('active');
}

function closeSurveyModal() {
    document.getElementById('surveyModal').classList.remove('active');
    document.getElementById('surveyForm').reset();
}

async function handleSurveySubmit(event) {
    event.preventDefault();
    
    const confirmCheckbox = document.getElementById('confirmService');
    if (!confirmCheckbox.checked) {
        alert('Please confirm that the service was completed.');
        return;
    }

    // Collect form data
    const taskDefinition = document.querySelector('input[name="task-definition"]:checked')?.value;
    const timeComparison = document.querySelector('input[name="time-comparison"]:checked')?.value;
    const consumerTags = Array.from(document.querySelectorAll('input[name="consumer-tags"]:checked'))
        .map(checkbox => checkbox.value);
    const comments = document.getElementById('surveyComments').value;
    
    const surveyData = {
        task_definition: taskDefinition,
        time_comparison: timeComparison,
        consumer_tags: consumerTags,
        comments: comments,
        confirmed: true,
        timestamp: new Date().toISOString()
    };

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/progress/${currentProgress.id}/submit-survey`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ survey_data: surveyData })
        });

        if (response.ok) {
            const result = await response.json();
            
            // Close modal
            closeSurveyModal();
            
            // Show success message
            alert(result.message);
            
            // Update balance if both parties completed
            if (result.completed) {
                await updateUserBalance();
            }
            
            window.location.reload();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to submit survey');
        }
    } catch (error) {
        console.error('Error submitting survey:', error);
        alert('Failed to submit survey');
    }
}

function reportIssue() {
    const issue = prompt('Describe the issue:');
    if (issue) {
        alert('Issue reported (demo). This would notify admins.');
    }
}

function leaveReview() {
    alert('Review feature coming soon!');
}

function formatStatus(status) {
    const statusMap = {
        'selected': 'Selected',
        'scheduled': 'Scheduled',
        'in_progress': 'In Progress',
        'awaiting_confirmation': 'Awaiting Confirmation',
        'completed': 'Completed'
    };
    return statusMap[status] || status;
}

function formatTime(timeStr) {
    if (!timeStr) return '';
    // Convert time to HH:MM format (remove seconds if present)
    return timeStr.split(':').slice(0, 2).join(':');
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
    });
}

function formatDateTime(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    const dateFormatted = date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric'
    });
    const timeFormatted = date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false
    });
    return `${dateFormatted} ${timeFormatted}`;
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-US', { 
        weekday: 'short',
        month: 'short', 
        day: 'numeric', 
        year: 'numeric'
    });
}

function toggleProposeScheduleForm() {
    const form = document.getElementById('proposeScheduleForm');
    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('proposalDate').min = today;
        
        // Display required hours
        if (currentService && currentService.hours_required) {
            document.getElementById('requiredHours').textContent = currentService.hours_required;
        }
    } else {
        form.style.display = 'none';
        // Clear form
        document.getElementById('proposalDate').value = '';
        document.getElementById('proposalStartTime').value = '';
        document.getElementById('proposalEndTime').value = '';
        document.getElementById('proposalLocation').value = '';
        document.getElementById('durationWarning').style.display = 'none';
    }
}

// Validate that the proposed duration matches the required hours
function validateDuration() {
    const startTime = document.getElementById('proposalStartTime').value;
    const endTime = document.getElementById('proposalEndTime').value;
    const warning = document.getElementById('durationWarning');
    const warningText = document.getElementById('durationWarningText');
    
    if (!startTime || !endTime || !currentService) {
        warning.style.display = 'none';
        return true;
    }
    
    // Calculate duration in hours
    const start = new Date(`2000-01-01T${startTime}`);
    const end = new Date(`2000-01-01T${endTime}`);
    const durationMs = end - start;
    const durationHours = durationMs / (1000 * 60 * 60);
    
    const serviceType = currentService.service_type || currentService.type;
    const requiredHours = currentService.hours_required;
    
    if (durationHours <= 0) {
        warningText.textContent = 'End time must be after start time.';
        warning.style.display = 'block';
        return false;
    }
    
    // For offers: flexible hours between 1-3, for needs: must match exactly
    if (serviceType === 'offer') {
        if (durationHours < 1) {
            warningText.textContent = 'Duration must be at least 1 hour for offers.';
            warning.style.display = 'block';
            return false;
        } else if (durationHours > 3) {
            warningText.textContent = 'Duration cannot exceed 3 hours for offers.';
            warning.style.display = 'block';
            return false;
        } else {
            warning.style.display = 'none';
            return true;
        }
    } else {
        // For needs: strict matching required
        if (Math.abs(durationHours - requiredHours) > 0.01) {
            warningText.textContent = `The estimated hours is ${requiredHours} hours. Proposed duration is ${durationHours.toFixed(1)} hours. Please adjust the times to match.`;
            warning.style.display = 'block';
            return false;
        } else {
            warning.style.display = 'none';
            return true;
        }
    }
}

// New function called from sidebar button
function openScheduleProposal() {
    // Check if service is cancelled
    if (currentProgress.status === 'cancelled') {
        alert('Cannot propose schedule for a cancelled service');
        return;
    }
    
    const form = document.getElementById('proposeScheduleForm');
    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('proposalDate').min = today;
        
        // Display required hours or range based on service type
        const serviceType = currentService ? (currentService.service_type || currentService.type) : null;
        const hoursInfoElement = document.getElementById('requiredHours');
        
        if (currentService && currentService.hours_required) {
            if (serviceType === 'offer') {
                hoursInfoElement.textContent = '1-3 hours (flexible)';
                hoursInfoElement.parentElement.innerHTML = '<strong>⏱️ Duration Range:</strong> <span id="requiredHours">1-3 hours (flexible)</span>';
            } else {
                hoursInfoElement.textContent = currentService.hours_required;
            }
        }
        
        // Scroll to form and center it in the viewport
        setTimeout(() => {
            form.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
    }
}

async function submitScheduleProposal() {
    // Check if there's already a pending proposal
    if (hasPendingProposal) {
        alert('There is already a pending schedule proposal. Please wait for a response or cancel the existing proposal before submitting a new one.');
        return;
    }

    const proposalDate = document.getElementById('proposalDate').value;
    const proposalStartTime = document.getElementById('proposalStartTime').value;
    const proposalEndTime = document.getElementById('proposalEndTime').value;
    const proposalLocation = document.getElementById('proposalLocation').value;

    if (!proposalDate || !proposalStartTime || !proposalEndTime) {
        alert('Please fill in date, start time, and end time');
        return;
    }

    // Validate duration matches required hours
    if (!validateDuration()) {
        const serviceType = currentService ? (currentService.service_type || currentService.type) : null;
        if (serviceType === 'offer') {
            alert('Please adjust the start and end times. Duration must be between 1-3 hours for offers.');
        } else {
            alert('Please adjust the start and end times to match the required duration.');
        }
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/progress/${currentProgress.id}/propose-schedule`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                proposed_date: proposalDate,
                proposed_start_time: proposalStartTime,
                proposed_end_time: proposalEndTime,
                proposed_location: proposalLocation || null
            })
        });

        if (response.ok) {
            const result = await response.json();
            alert('Schedule proposal sent successfully!');
            toggleProposeScheduleForm();
            loadMessages();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to send proposal');
        }
    } catch (error) {
        console.error('Error sending proposal:', error);
        alert('Failed to send schedule proposal');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    NavBar.init();
    await loadProgressData();
});

// Enter key to send message
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('messageInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
