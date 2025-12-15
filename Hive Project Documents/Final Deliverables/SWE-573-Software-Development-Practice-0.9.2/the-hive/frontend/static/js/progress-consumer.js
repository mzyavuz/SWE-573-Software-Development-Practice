// Progress tracking for Consumer (both Offer and Need)
const APPLICATION_ID = new URLSearchParams(window.location.search).get('application_id');
let currentProgress = null;
let currentApplication = null;
let currentService = null;
let otherUser = null;

// Use centralized BalanceManager if available, otherwise fall back to local function
async function updateUserBalance() {
    if (window.BalanceManager && window.BalanceManager.update) {
        return await window.BalanceManager.update();
    }
    
    // Fallback implementation if BalanceManager not loaded
    try {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        const response = await fetch('/api/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const data = await response.json();
            const userData = JSON.parse(localStorage.getItem('user') || '{}');
            userData.time_balance = data.user.time_balance;
            localStorage.setItem('user', JSON.stringify(userData));

            if (window.NavBar && window.NavBar.updateBalance) {
                window.NavBar.updateBalance(data.user.time_balance);
            }

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
            const errorText = await progressResponse.text();
            console.error('Progress API error:', progressResponse.status, errorText);
            throw new Error(`Failed to load progress: ${progressResponse.status}`);
        }

        const progressData = await progressResponse.json();
        currentProgress = progressData.progress;
        
        // Extract service info from progress data
        currentService = {
            id: currentProgress.service_id,
            title: currentProgress.service_title,
            type: currentProgress.service_type,
            created_at: currentProgress.service_created_at,
            location_address: currentProgress.location_address,
            service_date: currentProgress.service_date,
            start_time: currentProgress.start_time,
            end_time: currentProgress.end_time
        };
        
        // Extract other user info from progress data
        otherUser = {
            id: currentProgress.provider_id,
            full_name: currentProgress.provider_name,
            email: currentProgress.provider_name, // Use name as fallback
            balance: 0, // Not provided in API
            photo: currentProgress.provider_photo
        };
        
        // Application info is embedded in progress
        currentApplication = {
            id: currentProgress.application_id
        };

        renderProgressStepper();
        renderStatusAlert();
        renderProviderInfo();
        renderSidebarInfo();
        renderActionButtons();
        renderServiceDetails();
        loadMessages();
        checkReportedStatus();

    } catch (error) {
        console.error('Error loading progress:', error);
        document.getElementById('statusAlert').innerHTML = 
            '<strong>Error</strong><p style="margin-top: 0.5rem; font-size: 0.875rem;">Failed to load progress data.</p>';
    }
}

function renderProgressStepper() {
    const stepper = document.getElementById('progressStepper');
    if (!currentProgress) {
        stepper.innerHTML = '<p style="color: var(--text-light); text-align: center;">Loading progress...</p>';
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
    if (!currentService || !currentProgress) {
        alert.innerHTML = '<strong>Error</strong><p style="margin-top: 0.5rem; font-size: 0.875rem;">Service information not available.</p>';
        return;
    }
    const isOffer = currentService.type === 'offer';
    
    const formatTimeShort = (timeStr) => {
        if (!timeStr) return '';
        // If already contains HH:MM or HH:MM:SS, capture first two parts
        const match = timeStr.match(/(\d{1,2}):(\d{2})/);
        if (match) {
            const hh = match[1].padStart(2, '0');
            const mm = match[2];
            return `${hh}:${mm}`;
        }
        // Fallback: try parsing as Date
        const d = new Date(timeStr);
        if (!isNaN(d)) {
            const hh = String(d.getHours()).padStart(2, '0');
            const mm = String(d.getMinutes()).padStart(2, '0');
            return `${hh}:${mm}`;
        }
        return timeStr;
    };

    const statusMessages = {
        'selected': {
            class: 'info',
            title: '📅 Provider Selected',
            text: isOffer 
                ? 'Schedule a date and time for this service with the provider.'
                : 'The provider has been selected. They will schedule the service with you.'
        },
        'scheduled': {
            class: 'info',
            title: '⏰ Service Scheduled',
            text: `Service scheduled for ${formatDate(currentProgress.scheduled_date)} at ${formatTimeShort(currentProgress.scheduled_time)}. The provider will mark it as "In Progress" when they start.`
        },
        'in_progress': {
            class: 'info',
            title: '🔧 Service In Progress',
            text: 'The provider is working on your service. They will mark it as complete when finished.'
        },
        'awaiting_confirmation': {
            class: 'info',
            title: '⏰ Please Confirm Completion',
            text: 'The provider has marked the service as complete. Please confirm to complete the transaction.'
        },
        'completed': {
            class: 'success',
            title: '✅ Service Completed!',
            text: isOffer 
                ? `${currentProgress.hours} hours have been credited to your account.`
                : `${currentProgress.hours} hours have been deducted from your account.`
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

function renderProviderInfo() {
    const container = document.getElementById('providerInfo');
    if (!otherUser || !currentService) {
        container.innerHTML = '<p style="color: var(--text-light);">Loading provider information...</p>';
        return;
    }
    
    const initials = otherUser.full_name ? 
        otherUser.full_name.split(' ').map(n => n[0]).join('').toUpperCase() : 
        otherUser.email[0].toUpperCase();

    container.innerHTML = `
        <div class="provider-header">
            <div class="provider-avatar">${initials}</div>
            <div class="provider-details">
                <div class="provider-name">${otherUser.full_name || otherUser.email}</div>
            </div>
            <button class="btn btn-ghost" onclick="window.location.href='/user/${otherUser.id}'">View Profile</button>
        </div>
    `;
}

function renderSidebarInfo() {
    if (!currentProgress) return;
    
    document.getElementById('sidebarStatus').textContent = formatStatus(currentProgress.status);
    document.getElementById('selectedDate').textContent = formatDate(currentProgress.selected_at);
    const hoursNum = parseFloat(currentProgress.hours);
    const hoursText = hoursNum % 1 === 0 ? Math.round(hoursNum) : hoursNum.toFixed(1);
    const hourLabel = hoursNum === 1 ? 'hr' : 'hrs';
    document.getElementById('estimatedHours').textContent = `${hoursText} ${hourLabel}`;
    
    // Show actual location for needs, or agreed location if set
    const location = currentProgress.agreed_location || 
                    (currentService && currentService.type === 'need' && currentService.location) || 
                    'Not specified';
    document.getElementById('locationDistance').textContent = location;

    if (currentProgress.scheduled_date) {
        document.getElementById('scheduledDateRow').style.display = 'flex';
        document.getElementById('scheduledDate').textContent = formatDate(currentProgress.scheduled_date);
    }

    if (currentProgress.scheduled_time) {
        document.getElementById('scheduledTimeRow').style.display = 'flex';
        document.getElementById('scheduledTime').textContent = formatTimeShort(currentProgress.scheduled_time);
    }
}

function renderActionButtons() {
    const container = document.getElementById('actionButtons');
    if (!currentProgress || !currentService) {
        container.innerHTML = '';
        return;
    }
    
    // If service is cancelled, show no action buttons and disable messaging
    if (currentProgress.status === 'cancelled') {
        container.innerHTML = `
            <p style="font-size: 0.875rem; color: var(--text-light); text-align: center; padding: 1rem;">
                This service has been cancelled. No actions are available.
            </p>
        `;
        
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
    
    const isOffer = currentService.type === 'offer';
    const isNeed = currentService.type === 'need';
    const hasPendingProposal = currentProgress.proposed_by !== null;
    const proposedByMe = currentProgress.proposed_by === JSON.parse(atob(localStorage.getItem('access_token').split('.')[1])).user_id;
    const needsMyResponse = hasPendingProposal && !proposedByMe;
    
    let buttons = '';

    // Show pending proposal alert if exists
    if (hasPendingProposal) {
        const proposalInfo = `
            <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <strong>📋 Pending Schedule Proposal</strong>
                <div style="margin-top: 0.5rem; font-size: 0.875rem;">
                    <strong>Date:</strong> ${formatDate(currentProgress.proposed_date)}<br>
                    <strong>Time:</strong> ${currentProgress.proposed_time || 'Not specified'}<br>
                    ${currentProgress.proposed_location ? `<strong>Location:</strong> ${currentProgress.proposed_location}<br>` : ''}
                    <strong>Proposed by:</strong> ${proposedByMe ? 'You' : otherUser.full_name}
                </div>
            </div>
        `;
        buttons += proposalInfo;
        
        if (needsMyResponse) {
            buttons += `
            <button class="btn btn-ghost" style="width:100%; margin-bottom:0.5rem;" onclick="respondToProposal(false)">
                ❌ Reject Proposal
            </button>
            <button class="btn btn-primary" style="width:100%; margin-bottom:0.5rem;" onclick="respondToProposal(true)">
                ✅ Accept Proposal
            </button>
            `;
        } else {
            buttons += `
                <p style="font-size: 0.875rem; color: var(--text-light); font-style: italic; margin-bottom: 0.5rem;">
                    Waiting for ${otherUser.full_name || 'other party'} to respond...
                </p>
            `;
        }
    }

    switch(currentProgress.status) {
        case 'selected':
            if (!hasPendingProposal) {
                buttons += `
                    <button class="btn btn-primary" style="width:100%; margin-bottom:0.5rem;" onclick="openScheduleProposal()">
                        📅 ${isNeed ? 'Propose Schedule' : 'Schedule Service'}
                    </button>
                `;
            }
            break;
        case 'scheduled':
            // Check start confirmation status
            const providerStartConfirmed = currentProgress.provider_start_confirmed || false;
            const consumerStartConfirmed = currentProgress.consumer_start_confirmed || false;
            const isProvider = currentProgress.is_provider || false;
            
            if (!providerStartConfirmed && !consumerStartConfirmed) {
                // Neither party confirmed
                buttons += `
                    <button class="btn btn-primary" style="width:100%; margin-bottom:0.5rem;" onclick="confirmStart()">
                        ✅ Confirm Service Started
                    </button>
                `;
                if (!hasPendingProposal) {
                    buttons += `
                        <button class="btn btn-secondary" style="width:100%; margin-bottom:0.5rem;" onclick="openScheduleProposal()">
                            📅 Change Schedule
                        </button>
                    `;
                }
            } else if ((isProvider && providerStartConfirmed) || (!isProvider && consumerStartConfirmed)) {
                // Current user confirmed, waiting for other party
                buttons += `
                    <div class="alert alert-info" style="margin-bottom: 1rem; background: #d1ecf1; border: 1px solid #bee5eb; padding: 1rem; border-radius: 8px;">
                        <strong>✅ You confirmed service started</strong><br>
                        <span style="font-size: 0.875rem;">⏳ Waiting for ${isProvider ? 'consumer' : 'provider'} to confirm...</span>
                    </div>
                `;
                if (!hasPendingProposal) {
                    buttons += `
                        <button class="btn btn-secondary" style="width:100%; margin-bottom:0.5rem;" onclick="openScheduleProposal()">
                            📅 Change Schedule
                        </button>
                    `;
                }
            } else {
                // Other party confirmed, current user hasn't
                buttons += `
                    <div class="alert alert-warning" style="margin-bottom: 1rem; background: #fff3cd; border: 1px solid #ffc107; padding: 1rem; border-radius: 8px;">
                        <strong>⏳ ${isProvider ? 'Consumer' : 'Provider'} confirmed service started</strong><br>
                        <span style="font-size: 0.875rem;">Please confirm to start the service</span>
                    </div>
                    <button class="btn btn-primary" style="width:100%; margin-bottom:0.5rem;" onclick="confirmStart()">
                        ✅ Confirm Service Started
                    </button>
                `;
                if (!hasPendingProposal) {
                    buttons += `
                        <button class="btn btn-secondary" style="width:100%; margin-bottom:0.5rem;" onclick="openScheduleProposal()">
                            📅 Change Schedule
                        </button>
                    `;
                }
            }
            break;
        case 'in_progress':
            if (!hasPendingProposal) {
                buttons += `
                    <button class="btn btn-secondary" style="width:100%; margin-bottom:0.5rem;" onclick="openScheduleProposal()">
                        📅 Reschedule
                    </button>
                `;
            }
            buttons += `
                <p style="font-size: 0.875rem; color: var(--text-light); margin-top: 0.5rem;">
                    Service in progress. The provider will notify you when complete.
                </p>
            `;
            break;
        case 'awaiting_confirmation':
            buttons += `
                <button class="btn btn-primary" style="width:100%; margin-bottom:0.5rem;" onclick="confirmComplete()">
                    ✅ Confirm Completion
                </button>
                <button class="btn btn-ghost" style="width:100%;" onclick="reportIssue()">
                    ⚠️ Report Issue
                </button>
            `;
            break;
        case 'completed':
            buttons += `
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
    if (!currentProgress || !currentService) {
        container.innerHTML = '<p style="color: var(--text-light);">Loading service details...</p>';
        return;
    }
    
    const statusBadge = `<span class="status-badge status-${currentProgress.status}">${formatStatus(currentProgress.status)}</span>`;

    const hoursNum = parseFloat(currentProgress.hours);
    const hoursText = hoursNum % 1 === 0 ? Math.round(hoursNum) : hoursNum.toFixed(1);
    const hourLabel = hoursNum === 1 ? 'hour' : 'hours';

    // Build need details section if this is a need service
    let needDetailsHtml = '';
    if (currentService.type === 'need') {
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

    container.innerHTML = `
        <div class="status-header">
            <div>
                <h2 class="service-title" style="font-size: 1.25rem;">${currentService.title}</h2>
                <div class="service-meta">
                    ${currentService.type === 'offer' ? '💼 Offer' : '🙋 Need'} • ${hoursText} ${hourLabel}
                </div>
            </div>
            ${statusBadge}
        </div>
        ${needDetailsHtml}
        ${currentProgress.special_instructions ? `
            <p style="color: var(--text-light); margin-bottom: 1rem;">
                <strong>Special Instructions:</strong><br>
                ${currentProgress.special_instructions}
            </p>
        ` : ''}
        ${currentProgress.agreed_location ? `
            <p style="color: var(--text-light); margin-bottom: 1rem;">
                <strong>Agreed Location:</strong> ${currentProgress.agreed_location}
            </p>
        ` : ''}
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
                    <span class="proposal-details-value">${formatTimeShort(pendingProposal.proposal_start_time)} - ${formatTimeShort(pendingProposal.proposal_end_time)}</span>
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
                    <button class="btn-accept-proposal" onclick="respondToScheduleProposal(${pendingProposal.id}, true)">
                        ✓ Accept Proposal
                    </button>
                    <button class="btn-reject-proposal" onclick="respondToScheduleProposal(${pendingProposal.id}, false)">
                        ✗ Reject Proposal
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
                                <strong>Time:</strong> ${formatTimeShort(msg.proposal_start_time)} - ${formatTimeShort(msg.proposal_end_time)}
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
            
            // Get user balance
            const userData = JSON.parse(localStorage.getItem('user'));
            const currentBalance = userData.time_balance != null ? parseFloat(userData.time_balance) : 1.0;
            const afterBalance = currentBalance - scheduledHours;
            
            // Format hours for display
            const schedHoursText = scheduledHours % 1 === 0 ? Math.round(scheduledHours) : scheduledHours.toFixed(1);
            const currentBalanceText = currentBalance % 1 === 0 ? Math.round(currentBalance) : currentBalance.toFixed(1);
            const afterBalanceText = afterBalance % 1 === 0 ? Math.round(afterBalance) : afterBalance.toFixed(1);
            const needMoreText = (scheduledHours - currentBalance) % 1 === 0 ? Math.round(scheduledHours - currentBalance) : (scheduledHours - currentBalance).toFixed(1);
            
            // Build warning message
            let confirmMessage = `Accept this proposed schedule?\n\n`;
            confirmMessage += `📅 Proposed Schedule: ${message.proposal_date}\n`;
            confirmMessage += `⏰ Time: ${formatTimeShort(message.proposal_start_time)} - ${formatTimeShort(message.proposal_end_time)}\n`;
            confirmMessage += `⏱️ Duration: ${schedHoursText} ${scheduledHours === 1 ? 'hour' : 'hours'}\n\n`;
            confirmMessage += `Current Balance: ${currentBalanceText} ${currentBalance === 1 ? 'hour' : 'hours'}\n`;
            confirmMessage += `After Service: ${afterBalanceText} ${afterBalance === 1 ? 'hour' : 'hours'}\n\n`;
            
            if (currentBalance < scheduledHours) {
                confirmMessage += `⚠️ WARNING: You have ${currentBalanceText} ${currentBalance === 1 ? 'hour' : 'hours'} but this service requires ${schedHoursText} ${scheduledHours === 1 ? 'hour' : 'hours'}.\n`;
                confirmMessage += `You need ${needMoreText} more ${(scheduledHours - currentBalance) === 1 ? 'hour' : 'hours'} to proceed.\n\n`;
            } else if (afterBalance < 0.5) {
                confirmMessage += `⚠️ WARNING: Your balance will be very low (${afterBalanceText} ${afterBalance === 1 ? 'hour' : 'hours'}) after this service.\n\n`;
                confirmMessage += `Continue?`;
            } else {
                confirmMessage += `Continue with this schedule?`;
            }
            
            if (!confirm(confirmMessage)) return;
            
        } catch (error) {
            console.error('Error calculating schedule hours:', error);
            // Fallback to simple confirmation
            if (!confirm('Accept this proposed schedule? The service will proceed with these new times.')) return;
        }
    } else {
        if (!confirm('Reject this proposed schedule? This will cancel the progress and reopen the service to others. The rejected applicant will not be able to apply to this service again.')) return;
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
            alert(error.error || `Failed to ${action} schedule`);
        }
    } catch (error) {
        console.error(`Error ${action}ing schedule:`, error);
        alert(`Failed to ${action} schedule`);
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
            
            // Get user balance
            const userData = JSON.parse(localStorage.getItem('user'));
            const currentBalance = userData.time_balance != null ? parseFloat(userData.time_balance) : 1.0;
            const afterBalance = currentBalance - scheduledHours;
            
            // Format hours for display
            const schedHoursText = scheduledHours % 1 === 0 ? Math.round(scheduledHours) : scheduledHours.toFixed(1);
            const currentBalanceText = currentBalance % 1 === 0 ? Math.round(currentBalance) : currentBalance.toFixed(1);
            const afterBalanceText = afterBalance % 1 === 0 ? Math.round(afterBalance) : afterBalance.toFixed(1);
            const needMoreText = (scheduledHours - currentBalance) % 1 === 0 ? Math.round(scheduledHours - currentBalance) : (scheduledHours - currentBalance).toFixed(1);
            
            // Build warning message
            let confirmMessage = `Accept this proposed schedule?\n\n`;
            confirmMessage += `📅 Proposed Schedule: ${message.proposal_date}\n`;
            confirmMessage += `⏰ Time: ${formatTimeShort(message.proposal_start_time)} - ${formatTimeShort(message.proposal_end_time)}\n`;
            confirmMessage += `⏱️ Duration: ${schedHoursText} ${scheduledHours === 1 ? 'hour' : 'hours'}\n\n`;
            confirmMessage += `Current Balance: ${currentBalanceText} ${currentBalance === 1 ? 'hour' : 'hours'}\n`;
            confirmMessage += `After Service: ${afterBalanceText} ${afterBalance === 1 ? 'hour' : 'hours'}\n\n`;
            
            if (currentBalance < scheduledHours) {
                confirmMessage += `⚠️ WARNING: You have ${currentBalanceText} ${currentBalance === 1 ? 'hour' : 'hours'} but this service requires ${schedHoursText} ${scheduledHours === 1 ? 'hour' : 'hours'}.\n`;
                confirmMessage += `You need ${needMoreText} more ${(scheduledHours - currentBalance) === 1 ? 'hour' : 'hours'} to proceed.\n\n`;
            } else if (afterBalance < 0.5) {
                confirmMessage += `⚠️ WARNING: Your balance will be very low (${afterBalanceText} ${afterBalance === 1 ? 'hour' : 'hours'}) after this service.\n\n`;
                confirmMessage += `Continue?`;
            } else {
                confirmMessage += `Continue with this schedule?`;
            }
            
            if (!confirm(confirmMessage)) return;
            
        } catch (error) {
            console.error('Error calculating schedule hours:', error);
            // Fallback to simple confirmation
            if (!confirm('Accept this proposed schedule? The service will be scheduled with these details.')) return;
        }
    } else {
        if (!confirm('Reject this proposed schedule? This will cancel the progress and reopen the service to others. The rejected applicant will not be able to apply to this service again.')) return;
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
            alert(error.error || `Failed to ${action} schedule`);
        }
    } catch (error) {
        console.error(`Error ${action}ing schedule:`, error);
        alert(`Failed to ${action} schedule`);
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
                application_id: APPLICATION_ID
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

function toggleProposeScheduleForm() {
    const form = document.getElementById('proposeScheduleForm');
    if (form.style.display === 'none') {
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
    
    const requiredHours = currentService.hours_required;
    
    if (durationHours <= 0) {
        warningText.textContent = 'End time must be after start time.';
        warning.style.display = 'block';
        return false;
    } else if (Math.abs(durationHours - requiredHours) > 0.01) {
        const durationText = durationHours % 1 === 0 ? Math.round(durationHours) : durationHours.toFixed(1);
        const requiredText = requiredHours % 1 === 0 ? Math.round(requiredHours) : requiredHours.toFixed(1);
        warningText.textContent = `Duration is ${durationText} ${durationHours === 1 ? 'hour' : 'hours'}, but ${requiredText} ${requiredHours === 1 ? 'hour' : 'hours'} required. Please adjust the times.`;
        warning.style.display = 'block';
        return false;
    } else {
        warning.style.display = 'none';
        return true;
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
        
        // Display required hours
        if (currentService && currentService.hours_required) {
            document.getElementById('requiredHours').textContent = currentService.hours_required;
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
        alert('Please adjust the start and end times to match the required duration.');
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

async function confirmStart() {
    let confirmMessage = 'Confirm that the service has started?';
    
    // Add balance warning
    if (currentProgress) {
        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        const currentBalance = userData.time_balance != null ? parseFloat(userData.time_balance) : 1.0;
        const maxBalance = 10.0;
        const hours = parseFloat(currentProgress.hours) || 0;
        const isProvider = currentProgress.is_provider;
        const isConsumer = !isProvider;
        
        // Format values for display
        const balanceText = currentBalance % 1 === 0 ? Math.round(currentBalance) : currentBalance.toFixed(1);
        const hoursText = hours % 1 === 0 ? Math.round(hours) : hours.toFixed(1);
        const maxBalanceText = maxBalance % 1 === 0 ? Math.round(maxBalance) : maxBalance.toFixed(1);
        
        // Warn consumer about insufficient balance
        if (isConsumer && currentBalance < hours) {
            const shortage = hours - currentBalance;
            const shortageText = shortage % 1 === 0 ? Math.round(shortage) : shortage.toFixed(1);
            confirmMessage += `\n\n⚠️ WARNING: You have ${balanceText} ${currentBalance === 1 ? 'hour' : 'hours'} but this service requires ${hoursText} ${hours === 1 ? 'hour' : 'hours'}. You need ${shortageText} more ${shortage === 1 ? 'hour' : 'hours'}. The service cannot start until you have sufficient balance.`;
        }
        
        // Warn provider about exceeding maximum
        if (isProvider && (currentBalance + hours) > maxBalance) {
            const afterBalance = currentBalance + hours;
            const excess = afterBalance - maxBalance;
            const afterBalanceText = afterBalance % 1 === 0 ? Math.round(afterBalance) : afterBalance.toFixed(1);
            const excessText = excess % 1 === 0 ? Math.round(excess) : excess.toFixed(1);
            confirmMessage += `\n\n⚠️ WARNING: Completing this service will give you ${afterBalanceText} ${afterBalance === 1 ? 'hour' : 'hours'}, exceeding the ${maxBalanceText}-hour limit by ${excessText} ${excess === 1 ? 'hour' : 'hours'}. The service cannot start until this is resolved.`;
        }
        
        // Add balance info for both
        confirmMessage += `\n\nYour current balance: ${balanceText} ${currentBalance === 1 ? 'hour' : 'hours'}`;
        if (isConsumer) {
            const afterBalance = currentBalance - hours;
            const afterBalanceText = afterBalance % 1 === 0 ? Math.round(afterBalance) : afterBalance.toFixed(1);
            confirmMessage += `\nAfter service: ${afterBalanceText} ${afterBalance === 1 ? 'hour' : 'hours'}`;
        } else {
            const afterBalance = currentBalance + hours;
            const afterBalanceText = afterBalance % 1 === 0 ? Math.round(afterBalance) : afterBalance.toFixed(1);
            confirmMessage += `\nAfter service: ${afterBalanceText} ${afterBalance === 1 ? 'hour' : 'hours'}`;
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
            
            // Reload progress data
            await loadProgressData();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to confirm start');
        }
    } catch (error) {
        console.error('Error confirming start:', error);
        alert('Failed to confirm service start');
    }
}

async function confirmComplete() {
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
            <span class="summary-label">Provider</span>
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
            <span class="summary-label">Hours</span>
            <span class="summary-value">${hoursDisplay} ${hours === 1 ? 'hour' : 'hours'}</span>
        </div>
        <div class="summary-row highlight">
            <span class="summary-label">Time Credits to Transfer</span>
            <span class="summary-value">${hoursDisplay} ${hours === 1 ? 'hour' : 'hours'}</span>
        </div>
    `;
    document.getElementById('surveySummary').innerHTML = summaryHtml;
    
    // Populate warning
    const warningHtml = `
        <p><strong>⚠️ Important:</strong> Once you confirm completion, ${hoursDisplay} time ${hours === 1 ? 'credit' : 'credits'} will be transferred to ${otherUser.full_name}. This action cannot be undone. If there are any issues, please report them before confirming.</p>
    `;
    document.getElementById('surveyWarning').innerHTML = warningHtml;
    
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
        alert('Please confirm that the service was completed as agreed.');
        return;
    }

    // Collect form data
    const selectedTags = Array.from(document.querySelectorAll('input[name="tags"]:checked'))
        .map(checkbox => checkbox.value);
    const comments = document.getElementById('surveyComments').value;
    
    const surveyData = {
        confirmed: true,
        tags: selectedTags,
        comments: comments,
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
            
            if (result.completed) {
                // Both parties completed, reload to show final status
                window.location.reload();
            } else {
                // Waiting for other party
                window.location.reload();
            }
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to confirm completion');
        }
    } catch (error) {
        console.error('Error confirming completion:', error);
        alert('Failed to confirm completion');
    }
}

function showScheduleModal() {
    const date = currentProgress.proposed_date || currentProgress.scheduled_date || '';
    const time = currentProgress.proposed_time || currentProgress.scheduled_time || '';
    const location = currentProgress.proposed_location || currentProgress.agreed_location || '';
    
    const newDate = prompt('Enter scheduled date (YYYY-MM-DD):', date);
    if (!newDate) return;
    
    const newTime = prompt('Enter scheduled time (HH:MM):', time);
    if (!newTime) return;
    
    const newLocation = prompt('Enter location (optional):', location);

    proposeSchedule(newDate, newTime, newLocation);
}

async function proposeSchedule(date, time, location) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/progress/${currentProgress.id}/propose-schedule`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                proposed_date: date,
                proposed_time: time,
                proposed_location: location
            })
        });

        if (response.ok) {
            alert('Schedule proposal sent! Waiting for other party to accept.');
            window.location.reload();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to propose schedule');
        }
    } catch (error) {
        console.error('Error proposing schedule:', error);
        alert('Failed to propose schedule');
    }
}

async function respondToProposal(accept) {
    const action = accept ? 'accept' : 'reject';
    if (!confirm(`Are you sure you want to ${action} this schedule proposal?`)) return;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/progress/${currentProgress.id}/respond-schedule`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ accept })
        });

        if (response.ok) {
            const result = await response.json();
            if (result.both_accepted) {
                alert('Schedule accepted by both parties! Service is now scheduled.');
            } else if (accept) {
                alert('Schedule accepted. Waiting for other party to accept.');
            } else {
                alert('Schedule proposal rejected.');
            }
            window.location.reload();
        } else {
            const error = await response.json();
            alert(error.error || `Failed to ${action} proposal`);
        }
    } catch (error) {
        console.error(`Error ${action}ing proposal:`, error);
        alert(`Failed to ${action} proposal`);
    }
}

async function scheduleService(date, time) {
    // Deprecated - now using proposeSchedule
    await proposeSchedule(date, time, currentProgress.agreed_location);
}

function reportIssue() {
    // Check if service is cancelled
    if (currentProgress.status === 'cancelled') {
        alert('Cannot report issues for a cancelled service');
        return;
    }
    
    // Check if already reported
    const reportKey = `reported_app_${APPLICATION_ID}`;
    const reportedData = localStorage.getItem(reportKey);
    if (reportedData) {
        const reportInfo = JSON.parse(reportedData);
        alert(`You have already reported this service on ${new Date(reportInfo.timestamp).toLocaleDateString()} for: ${reportInfo.reason}`);
        return;
    }
    
    openReportModal();
}

function openReportModal() {
    // Check if modal already exists and remove it
    const existingModal = document.getElementById('reportModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modalHtml = `
        <div id="reportModal" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 10000; padding: 1rem;">
            <div style="background: white; border-radius: 12px; max-width: 500px; width: 90%; max-height: 90vh; overflow-y: auto; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);">
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 1.5rem; border-bottom: 1px solid #e5e7eb;">
                    <h2 style="margin: 0; font-size: 1.25rem; font-weight: 600;">⚠️ Report Issue</h2>
                    <button onclick="closeReportModal()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #6b7280; line-height: 1;">&times;</button>
                </div>
                <form id="reportForm" onsubmit="handleReportSubmit(event)" style="padding: 1.5rem;">
                    <div style="margin-bottom: 1.5rem;">
                        <label style="display: block; font-weight: 600; margin-bottom: 0.75rem; color: #111827;">Select Issue Category *</label>
                        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                            <label style="display: flex; align-items: center; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                <input type="radio" name="reason" value="No-show" required style="margin-right: 0.75rem;">
                                <span style="color: #111827;">No-show</span>
                            </label>
                            <label style="display: flex; align-items: center; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                <input type="radio" name="reason" value="Inappropriate behavior" required style="margin-right: 0.75rem;">
                                <span style="color: #111827;">Inappropriate behavior</span>
                            </label>
                            <label style="display: flex; align-items: center; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                <input type="radio" name="reason" value="Safety concern" required style="margin-right: 0.75rem;">
                                <span style="color: #111827;">Safety concern</span>
                            </label>
                            <label style="display: flex; align-items: center; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                <input type="radio" name="reason" value="Quality issue" required style="margin-right: 0.75rem;">
                                <span style="color: #111827;">Quality issue</span>
                            </label>
                            <label style="display: flex; align-items: center; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                <input type="radio" name="reason" value="Other" required style="margin-right: 0.75rem;">
                                <span style="color: #111827;">Other</span>
                            </label>
                        </div>
                    </div>
                    <div style="margin-bottom: 1.5rem;">
                        <label for="reportDescription" style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: #111827;">Description *</label>
                        <textarea id="reportDescription" name="description" required rows="4" placeholder="Please describe the issue in detail..." style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 6px; font-family: inherit; resize: vertical; font-size: 0.875rem;"></textarea>
                    </div>
                    <div style="display: flex; gap: 0.75rem; justify-content: flex-end;">
                        <button type="button" onclick="closeReportModal()" class="btn btn-ghost" style="padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">Cancel</button>
                        <button type="submit" class="btn btn-primary" style="padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">Submit Report</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

function closeReportModal() {
    const modal = document.getElementById('reportModal');
    if (modal) {
        modal.remove();
    }
}

async function handleReportSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const reason = form.querySelector('input[name="reason"]:checked')?.value;
    const description = form.querySelector('#reportDescription').value.trim();
    
    if (!reason || !description) {
        alert('Please fill in all required fields');
        return;
    }
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/reports', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content_type: 'message',
                content_id: APPLICATION_ID,
                reported_user_id: otherUser.id,
                reason: reason,
                description: description
            })
        });

        if (response.ok) {
            closeReportModal();
            
            // Store reported status in localStorage
            const reportKey = `reported_app_${APPLICATION_ID}`;
            const reportInfo = {
                timestamp: new Date().toISOString(),
                reason: reason,
                reported_user_id: otherUser.id
            };
            localStorage.setItem(reportKey, JSON.stringify(reportInfo));
            
            // Update UI to show reported status
            updateReportButtonStatus(reportInfo);
            
            alert('Issue reported successfully. An administrator will review your report.');
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to submit report');
        }
    } catch (error) {
        console.error('Error reporting issue:', error);
        alert('Failed to submit report. Please try again.');
    }
}

function checkReportedStatus() {
    const reportKey = `reported_app_${APPLICATION_ID}`;
    const reportInfo = localStorage.getItem(reportKey);
    if (reportInfo) {
        updateReportButtonStatus(JSON.parse(reportInfo));
    }
}

function updateReportButtonStatus(reportInfo) {
    const reportBtn = document.querySelector('button[onclick="reportIssue()"]');
    if (reportBtn) {
        reportBtn.disabled = true;
        reportBtn.innerHTML = '✅ Issue Reported';
        reportBtn.style.opacity = '0.6';
        reportBtn.style.cursor = 'not-allowed';
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

function formatTimeShort(timeStr) {
    if (!timeStr) return '';
    // If already contains HH:MM or HH:MM:SS, capture first two parts
    const match = timeStr.match(/(\d{1,2}):(\d{2})/);
    if (match) {
        const hh = match[1].padStart(2, '0');
        const mm = match[2];
        return `${hh}:${mm}`;
    }
    // Fallback: try parsing as Date
    const d = new Date(timeStr);
    if (!isNaN(d)) {
        const hh = String(d.getHours()).padStart(2, '0');
        const mm = String(d.getMinutes()).padStart(2, '0');
        return `${hh}:${mm}`;
    }
    return timeStr;
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
    return new Date(dateStr).toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
    });
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

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadProgressData();
});

// Enter key to send message
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('messageInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
