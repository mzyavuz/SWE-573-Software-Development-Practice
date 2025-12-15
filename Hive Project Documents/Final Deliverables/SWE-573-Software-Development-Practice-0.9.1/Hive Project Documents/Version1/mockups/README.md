# Hive Time Banking Platform - Mockups

This folder contains all HTML mockups, CSS stylesheets, and JavaScript files for the Hive Time Banking Platform.

## 📁 Folder Structure

```
mockups/
├── css/
│   └── styles.css               # Main stylesheet with all component styles
├── index.html                   # Homepage with search, browse, and features
├── signin-mockup.html           # Sign In page (standalone)
├── signup-mockup.html           # Sign Up page (standalone)
├── profile-mockup.html          # User Profile page with activity, offers, needs, reviews, and settings
├── create-service-mockup.html   # Create Offer/Need form page
└── services-map.html     # Services map view with list and clustered markers
```

## 🎨 Design System

### Color Palette
- **Primary**: `#f59e0b` (Amber)
- **Primary Dark**: `#d97706`
- **Secondary**: `#10b981` (Green)
- **Text Dark**: `#1f2937`
- **Text Light**: `#6b7280`
- **Background Light**: `#f9fafb`
- **White**: `#ffffff`

### Typography
- **Font Family**: System fonts (Apple, Segoe UI, Roboto, etc.)
- **Headings**: Bold, 1.75rem - 3.5rem
- **Body**: Regular, 1rem
- **Small Text**: 0.875rem

## 🧩 Components

### Navigation
- Sticky header with logo, Offers/Needs toggle, and auth buttons
- Search bar integrated into navigation
- Responsive mobile design

### Modals
- Sign In modal with email/password fields
- Sign Up modal with full registration form
- Smooth animations and backdrop
- Close on click outside or Escape key

### Cards
- Service/offer cards with hover effects
- Feature cards with icons
- Result cards in grid layout

### Profile Components
- Profile header with user information and avatar
- Time bank balance card with prominent display
- Statistics dashboard with grid layout
- Activity feed with transaction history
- Tabbed navigation for different profile sections
- Editable settings forms
- Review display with ratings

## 📄 Pages

### index.html - Homepage
- Airbnb-style search bar integrated into navigation
- Browse section with filtering options (tags, distance, hours)
- Featured services grid
- How it works section
- Call-to-action section

### signin-mockup.html - Sign In
- Email and password fields
- Forgot password link
- Modal and standalone page versions

### signup-mockup.html - Sign Up
- Full name fields
- Date of birth (dropdown selectors: day, month, year)
- Email and password fields
- Age verification (13+ requirement)
- Parental consent for users under 16
- Email verification modal

### create-service-mockup.html - Create Offer/Need
- Service type selector (Offer vs Need)
- Basic information (title, description, hours, category)
- Location and delivery method selection
- Tag management system with suggested tags
- Availability scheduling (for Offers)
- Deadline and urgency settings (for Needs)
- Draft saving functionality
- Form validation and character counters
- Back button with unsaved changes confirmation

### services-map.html - Map View
- **Split Screen Layout**: Services list (left) and map (right)
- **Interactive Map**: Clustered markers showing service locations
  - Individual markers (number 1) for single services
  - Cluster markers (number 3+) for multiple services in same area
  - Active state highlighting for selected services
- **Filters Panel**:
  - Search bar for text-based filtering
  - Tag filters (gardening, tutoring, moving, cooking, tech)
  - Distance filters (< 2km, < 5km, < 10km, All)
  - Duration filters (< 1hr, 1-2hrs, 2-4hrs, 4+ hrs)
- **Service Cards**: Compact view with key information
  - Title, provider, type badge (Offer/Need)
  - Description preview (2 lines)
  - Meta info (duration, location, rating/urgency)
  - Tags and distance display
- **Map Controls**: Zoom in/out, center, location
- **Synchronized Selection**: Clicking card highlights marker, clicking marker scrolls to card
- **Cluster Interaction**: Clicking cluster marker highlights all services in that area
- **View Toggle**: Switch between Map View and List View
- **Responsive**: Mobile-friendly with stacked layout
- Parental consent for users under 16
- Terms of service agreement
- Email verification flow

### profile-mockup.html - User Profile
- **Activity Tab**: Recent transactions and time credits earned/spent
- **Ongoing Services Tab**: Active service exchanges with 5-step status tracking
  - Visual progress tracker (Open → Provider Selected → In Progress → Awaiting Confirmation → Completed)
  - Partner information and messaging
  - Status-specific action buttons
  - Auto-confirmation timer display
- **My Offers Tab**: Services user provides with status management
- **My Needs Tab**: Services user is seeking with response tracking
- **Reviews Tab**: Ratings and feedback from other users
- **Settings Tab**: Profile editing, notification preferences, account actions
- Time bank balance display
- Statistics dashboard (services completed, received, active offers/needs)

### Forms
- Styled input fields with focus states
- Validation and error handling
- Checkbox groups with terms/privacy links

### Filters
- Browse tabs (All Services/Offers/Needs)
- Category, Distance, Hours, and Tags filters
- Responsive filter layout

## 🚀 Usage

### Viewing the Mockups
1. Open `index.html` in a web browser to see the homepage
2. Click "Sign In" or "Sign Up" buttons to see modal forms
3. Standalone signin/signup pages are also available

### Linking CSS
The homepage uses an external CSS file:
```html
<link rel="stylesheet" href="css/styles.css">
```

**Note**: JavaScript is kept inline within the HTML files for simplicity.

### Customization
- Edit colors in `:root` variables in `styles.css`
- Modify component styles in their respective sections
- Update JavaScript behavior directly in the HTML `<script>` tags

## 📱 Responsive Breakpoints

- **Desktop**: > 768px (default)
- **Tablet/Mobile**: ≤ 768px
  - Stacked search fields
  - Hidden navigation links
  - Single column filter groups
  - Responsive grid layouts

## 🔧 Future Enhancements

- [ ] Add backend API integration
- [ ] Implement actual search functionality
- [ ] Add real-time filtering
- [ ] Connect to database
- [ ] Add user authentication
- [ ] Implement map view for services
- [ ] Add messaging system
- [ ] Create user dashboard

## 📝 Notes

- All forms currently use placeholder functions
- Backend integration points are marked with `// TODO:` comments
- Console logs are included for debugging
- Social login buttons are included but not functional

---

**Last Updated**: October 2025
**Version**: 1.0.0
