# Scenario 7: Community Forum (The Commons)

**Feature:** Feature 12 – Community Forum (The Commons)

**User Story:**
> As a **Registered User**, I want to **participate in discussion threads within specific categories** so that **I can share ideas, ask general questions, and build relationships with my neighbors**.

---

## Overview

This scenario demonstrates the community forum feature called "The Commons" - a digital town square where users can engage in discussions outside of specific service transactions. The forum facilitates social trust and community building, which are essential for a successful TimeBank economy.

---

## Mockup Files

### HTML Mockups

Located in: `html/`

1. **the-commons-main.html** - Forum Categories Landing Page
   - Displays all admin-defined forum categories
   - Shows category descriptions, statistics, and latest activity
   - Includes community guidelines
   - Search functionality for discussions

2. **category-view.html** - Category Thread List View
   - Shows all discussion threads within a category
   - Thread sorting options (latest activity, most replies, newest, oldest)
   - Thread statistics (views, replies, last activity)
   - Pinned and locked thread indicators
   - "New Thread" creation button

3. **thread-view.html** - Individual Thread Discussion View
   - Displays original post and all replies
   - Numbered post system for easy reference
   - Thread actions (follow, report)
   - Post actions (reply, like)
   - Reply composition form at the bottom
   - Author avatars and timestamps

4. **new-thread.html** - Thread Creation Form
   - Category selection dropdown
   - Thread title input (150 character limit)
   - Rich text editor with formatting toolbar
   - Markdown support for formatting
   - Preview functionality
   - Community guidelines reminder
   - Character counters

### PDF Mockups

Located in: `pdf/`

PDF versions of all HTML mockups will be generated and placed here for documentation and presentation purposes.

---

## User Journey

### Main Flow: Participating in a Discussion

1. **Discover The Commons**
   - User navigates to "The Commons" from main navigation
   - Views forum categories landing page (`the-commons-main.html`)
   - Sees 6 categories with activity statistics

2. **Browse Category**
   - User selects "General Chat" category
   - Views category with active threads (`category-view.html`)
   - Sees pinned welcome thread and recent discussions
   - Sorts by latest activity, most replies, or date

3. **Read Thread**
   - User clicks on interesting thread "What's everyone's favorite local coffee spot?"
   - Views original post and all replies (`thread-view.html`)
   - Reads recommendations from community members
   - Sees conversation building organically

4. **Participate in Discussion**
   - User scrolls to reply section
   - Writes response sharing their own favorite coffee spot
   - Posts reply to contribute to the conversation

### Alternative Flow: Starting a New Discussion

1. **Create New Thread**
   - From category view, user clicks "New Thread" button
   - Lands on thread creation form (`new-thread.html`)
   - Selects appropriate category
   - Writes clear, descriptive title
   - Composes message using formatting toolbar

2. **Preview and Post**
   - User clicks "Preview" to see how thread will appear
   - Reviews content and formatting
   - Makes any necessary edits
   - Clicks "Post Thread" to publish

---

## Key Features Demonstrated

### Forum Structure
- **Categories**: Admin-defined categories for organized discussions
- **Threads**: User-created discussion topics within categories
- **Posts**: Individual messages within a thread (original post + replies)

### Thread Management
- **Pinned Threads**: Important threads stay at the top of categories
- **Locked Threads**: Admins can prevent further comments on resolved/finalized discussions
- **Thread Statistics**: Views, reply count, last activity timestamp

### User Interactions
- **Creating Threads**: Title + body with rich text formatting
- **Replying**: Add comments to existing discussions
- **Liking**: Express appreciation for helpful posts
- **Following**: Subscribe to thread updates
- **Reporting**: Flag inappropriate content for moderators

### Moderation Features
- **Admin Controls**: Lock threads, pin important topics
- **Community Guidelines**: Clear rules displayed prominently
- **Report System**: Users can flag content for review
- **Content Visibility**: Admins manage what appears in categories

### Social Elements
- **Author Attribution**: Clear display of who posted what
- **Timestamps**: Relative time ("15 minutes ago") for recent activity
- **User Avatars**: Visual identification of participants
- **Latest Activity**: Shows most recent contributor to threads

---

## Design Elements

### Visual Hierarchy
- **Category Icons**: Emoji icons for quick category identification (💬 📢 🤝 ❓ 📖 💡)
- **Status Badges**: Pinned (📌) and Locked (🔒) indicators
- **Gradients**: Purple gradient headers for The Commons identity
- **Color Coding**: Consistent with main Hive brand (amber primary color)

### User Experience
- **Breadcrumb Navigation**: Easy navigation back through forum hierarchy
- **Character Counters**: Real-time feedback on title/body length
- **Formatting Toolbar**: Visual buttons for common markdown formatting
- **Preview Functionality**: See how thread will appear before posting
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Accessibility
- **Clear Labels**: All form fields properly labeled
- **Action Buttons**: Descriptive button text (not just icons)
- **Keyboard Navigation**: All interactive elements keyboard accessible
- **Color Contrast**: Meets WCAG standards

---

## Acceptance Criteria Coverage

✅ **Given a logged-in user, when they access The Commons, then they see a list of Admin-defined Forum Categories**
- Demonstrated in `the-commons-main.html` with 6 categories

✅ **Given a user is viewing a Category, when they click "New Thread," then they can compose a title and body text**
- Demonstrated in `new-thread.html` with complete creation form

✅ **Given a created thread, when other users view it, then they can add comments to the discussion**
- Demonstrated in `thread-view.html` with reply form at bottom

✅ **Given a user is the author of a post or thread, when they select edit/delete, then the content is updated or removed accordingly**
- Edit/delete buttons shown in post action menus (implementation pending)

✅ **Given a thread contains inappropriate content, when a user clicks "Report," then the thread is flagged for Admin review**
- Report button available in thread header actions

✅ **Given a guest user (Neighbor), when they attempt to post or comment, then they are redirected to the registration page**
- User must be logged in (shown by avatar in nav) to access The Commons

---

## Technical Implementation Notes

### Functional Requirements Addressed

| FR-12.1 | Display list of Forum Categories managed by Admins | ✅ Main page |
| FR-12.2 | Users can create new Discussion Threads within a category | ✅ New thread form |
| FR-12.3 | Users can post Comments on existing threads | ✅ Reply form |
| FR-12.4 | Support rich text formatting (Markdown) | ✅ Toolbar + markdown |
| FR-12.5 | Users can edit or delete own posts and threads | ⚠️ Buttons shown |
| FR-12.6 | Display "Last Activity" timestamp for each thread | ✅ All lists |
| FR-12.7 | Users can Report threads or comments | ✅ Report buttons |
| FR-12.8 | Admins can lock threads | ✅ Locked indicator |
| FR-12.9 | Admins can pin threads | ✅ Pinned threads shown |
| FR-12.10 | Search keywords within The Commons | ⚠️ Search bar present |

### Data Model Requirements

**ForumCategory**
- category_id, name, description, icon emoji
- created_by (admin), is_active
- Statistics: thread count, post count

**Thread**
- thread_id, category_id, author_id
- title, body, is_pinned, is_locked, status
- created_at, updated_at, last_activity_at
- Statistics: view count, reply count

**Post** (Comments)
- post_id, thread_id, author_id
- body, parent_post_id (for nested replies)
- is_deleted, created_at, updated_at
- Like count

---

## Future Enhancements

### Phase 2 Features
- **Nested Replies**: Comments on comments (not just thread-level)
- **Rich Media**: Image uploads, embedded links with previews
- **Notifications**: Alert users when their threads receive replies
- **User Mentions**: @username tagging for direct mentions
- **Thread Subscriptions**: Email updates for followed threads
- **Advanced Search**: Filter by date range, author, tags
- **Post Editing History**: Track edits and show "edited" badge
- **Reaction Emojis**: Beyond just likes (👍 ❤️ 😂 🎉)

### Moderation Tools
- **Automated Filters**: Profanity detection
- **User Reporting Dashboard**: Admin view of all reports
- **Warning System**: Issue warnings before banning
- **Thread Moving**: Relocate threads to different categories
- **Mass Actions**: Bulk delete spam, lock multiple threads

---

## Related Documentation

- **Software Requirements Specification**: Section 3.12 - Feature 12
- **Use Cases**: Community Forum usage scenarios
- **Admin Dashboard**: Forum moderation features
- **User Profile**: Integration with user identity and reputation

---

## Notes for Developers

### Implementation Priority
1. **Basic Thread Creation/Viewing** (High)
2. **Replying to Threads** (High)
3. **Category Management** (High)
4. **Search Functionality** (Medium)
5. **Rich Text Formatting** (Medium)
6. **Nested Replies** (Low)

### Security Considerations
- **XSS Prevention**: Sanitize all user input
- **Rate Limiting**: Prevent spam posting
- **Content Moderation**: Queue for admin review if needed
- **Authentication**: Verify user logged in for all post/comment actions

### Performance Considerations
- **Pagination**: Limit threads per page (shown: 6 threads)
- **Lazy Loading**: Load posts as user scrolls
- **Caching**: Cache category statistics
- **Database Indexing**: Index on category_id, author_id, timestamps

---

**Created:** December 9, 2024
**Version:** 1.0
**Status:** Complete - Ready for development reference
