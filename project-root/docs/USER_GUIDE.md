# User Guide

Complete guide for using the Real-Time Collaborative Drawing Application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Registration and Login](#registration-and-login)
3. [Room Management](#room-management)
4. [Drawing Tools](#drawing-tools)
5. [Collaboration Features](#collaboration-features)
6. [Tips and Best Practices](#tips-and-best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Accessing the Application

1. Open your web browser (Chrome, Firefox, Safari, or Edge recommended)
2. Navigate to `http://localhost:3000` (or your deployed URL)
3. You'll see the login/registration screen

### System Requirements

- Modern web browser with JavaScript enabled
- Stable internet connection for real-time features
- Screen resolution: 1024x768 or higher recommended

---

## Registration and Login

### Creating an Account

1. Click the **"Register"** tab on the home screen
2. Fill in the registration form:
   - **Email**: Your email address (used as username)
   - **Password**: Secure password (minimum 6 characters recommended)
   - **Full Name**: Your display name (optional)
3. Click **"Register"** button
4. Upon success, you'll see a confirmation message
5. Switch to **"Login"** tab to sign in

**Note**: Email addresses must be unique. If the email is already registered, you'll receive an error message.

---

### Logging In

1. Enter your registered email address
2. Enter your password
3. Click **"Login"** button
4. Upon successful authentication, you'll be redirected to the Room Selection screen

**Forgot Password?**: Currently, password recovery is not implemented. Contact your administrator for assistance.

---

## Room Management

### Creating a New Room

1. After logging in, you'll see the Room Selection interface
2. Click the **"Create Room"** tab
3. Fill in the room details:
   - **Room Name**: Descriptive name for your room (e.g., "Design Team Workspace")
   - **Description**: Optional details about the room's purpose
   - **Max Users**: Maximum number of users allowed (default: 10)
4. Click **"Create Room"**
5. You'll be automatically entered into the room as the **owner**

**Room ID**: Each room gets a unique ID (e.g., `room-a1b2c3d4`). Share this ID with others to invite them.

---

### Joining an Existing Room

1. From the Room Selection screen, click the **"Join Room"** tab
2. Enter the **Room ID** provided by the room owner
3. Click **"Join Room"**
4. You'll enter the room as a **member**

**Note**: You must be invited by the room owner and have the correct room ID to join.

---

### Viewing Your Rooms

1. The **"My Rooms"** tab shows all rooms you're a member of
2. Each room displays:
   - Room name and description
   - Your role (Owner or Member)
   - Number of current members
   - Creation date
3. Click **"Enter Room"** to start drawing

---

### Room Roles

**Owner**:
- Full control over the room
- Can clear the canvas
- Can remove members
- Can delete the room
- Automatically assigned when creating a room

**Member**:
- Can draw and view the canvas
- Can see other users' cursors
- Can leave the room at any time
- Cannot modify room settings

---

## Drawing Tools

### Toolbar Overview

The drawing toolbar is located on the left side of the canvas and contains:

1. **Brush** - Freehand drawing
2. **Eraser** - Remove strokes
3. **Rectangle** - Draw rectangles
4. **Ellipse** - Draw ovals/circles
5. **Text** - Add text annotations
6. **Undo** - Clear canvas (owner only)

---

### Using the Brush Tool

1. Click the **Brush** icon (brush symbol)
2. Select a **color** from the color palette
3. Choose a **thickness** (2px - 12px)
4. Click and drag on the canvas to draw
5. Release to finish the stroke

**Tips**:
- Use thinner brushes for detailed work
- Use thicker brushes for bold strokes
- Selected color applies to all subsequent strokes

---

### Using the Eraser

1. Click the **Eraser** icon
2. Choose eraser size using the thickness selector
3. Click and drag over areas to erase
4. The eraser removes your own and others' strokes

**Note**: Eraser actions are immediately synced to all users.

---

### Drawing Shapes

#### Rectangle

1. Click the **Rectangle** icon
2. Select color and thickness
3. Click on the canvas to set the starting corner
4. Drag to the opposite corner
5. Release to complete the rectangle

#### Ellipse

1. Click the **Ellipse** icon
2. Select color and thickness
3. Click to set the center point
4. Drag to define width and height
5. Release to complete the ellipse

**Tips**:
- Hold position for perfect circles (ellipse with equal dimensions)
- Shapes are outlined, not filled

---

### Adding Text

1. Click the **Text** icon
2. Select text color
3. Click on the canvas where you want to place text
4. Type your text in the prompt dialog
5. Click **OK** to place the text

**Text Properties**:
- Font: System default
- Size: Based on selected thickness
- Color: Selected from color palette

---

### Color Palette

Available colors:
- **Red** (#e53e3e)
- **Blue** (#3182ce)
- **Green** (#38a169)
- **Orange** (#f6ad55)
- **Dark Gray** (#2d3748)
- **Gray** (#555)

**Changing Colors**:
- Click any color in the palette
- The selected color applies to the current tool
- Border indicates active color selection

---

### Thickness Options

Available thicknesses: 2px, 4px, 6px, 8px, 12px

**Selecting Thickness**:
- Click on thickness circles in the toolbar
- Selected thickness is highlighted
- Applies to brush, eraser, and shapes

---

## Collaboration Features

### Real-Time Drawing

All drawing actions are **instantly synchronized** across all users:
- When you draw, others see it immediately
- When others draw, you see their strokes in real-time
- No manual refresh required

---

### Cursor Tracking

You can see other users' cursors on the canvas:
- Each user's cursor shows their email/name
- Cursors move in real-time as users interact
- Helps coordinate collaborative work

**Cursor Colors**: Each user gets a distinct cursor color for easy identification.

---

### Collision Detection

When two users draw close to each other:
- Visual warning appears (yellow glow effect)
- Helps prevent accidental overlapping
- Allows better coordination

**Distance Threshold**: Warning triggers when cursors are within 50 pixels.

---

### Member List

The member panel shows:
- Total number of users in the room
- List of all connected users
- User roles (Owner/Member)
- Real-time updates when users join or leave

---

### Canvas Persistence

The canvas state is **automatically saved**:
- When you draw, changes are saved to the database
- When you rejoin a room, previous work is restored
- No manual save required

**Note**: Canvas is loaded from the latest snapshot when entering a room.

---

## Room Owner Features

### Clearing the Canvas

**Owner Only**: Only the room owner can clear the entire canvas.

1. Click the **Undo** icon (trash can symbol)
2. Confirm the action in the dialog
3. Canvas is cleared for all users
4. Action is immediately synced

**Warning**: This action cannot be undone and affects all users.

---

### Removing Members

**Owner Only**: Remove a member from the room.

1. Go to the member list
2. Find the member you want to remove
3. Click **"Remove"** next to their name
4. Confirm the action
5. Member is immediately disconnected

**Note**: Removed members can rejoin if they have the room ID.

---

### Leaving/Deleting Room

**Members**: Can leave at any time using the **"Leave Room"** button.

**Owner**: Has two options:
1. **Delete Room**: Permanently deletes the room and disconnects all members
2. **Transfer Ownership** (if implemented): Assign another member as owner before leaving

---

## Tips and Best Practices

### Effective Collaboration

1. **Communicate**: Use external chat or video to coordinate
2. **Divide Areas**: Assign different canvas sections to different users
3. **Use Colors**: Assign specific colors to team members for clarity
4. **Watch Cursors**: Monitor other users' cursor positions to avoid collisions
5. **Save Regularly**: Create manual snapshots of important work (if implemented)

---

### Performance Tips

1. **Stable Connection**: Use wired internet or strong WiFi
2. **Browser Choice**: Chrome and Firefox offer best performance
3. **Close Tabs**: Reduce browser memory usage
4. **Refresh**: If experiencing lag, refresh the page to reconnect

---

### Drawing Tips

1. **Smooth Strokes**: Draw slowly for more precise lines
2. **Layering**: Build complex drawings in layers
3. **Eraser Size**: Match eraser size to what you're removing
4. **Test First**: Try colors/thickness before committing to large areas
5. **Zoom Browser**: Use browser zoom (Ctrl/Cmd +/-) for detailed work

---

## Troubleshooting

### Cannot Login

**Problem**: Login fails with error message

**Solutions**:
- Verify email and password are correct
- Ensure account is registered
- Check if backend server is running
- Clear browser cache and try again

---

### Room Not Loading

**Problem**: Canvas doesn't appear after joining room

**Solutions**:
- Refresh the page
- Verify room ID is correct
- Check if you're still a member (owner may have removed you)
- Ensure WebSocket connection is established

---

### Drawing Not Syncing

**Problem**: Your drawings don't appear for other users

**Solutions**:
- Check internet connection
- Verify WebSocket connection in browser console (F12)
- Refresh the page to reconnect
- Try leaving and rejoining the room

---

### Cannot See Other Users

**Problem**: Other users' cursors or drawings are invisible

**Solutions**:
- Verify other users are actually online
- Check WebSocket connection
- Refresh the page
- Ensure you're in the same room

---

### Canvas Cleared Unexpectedly

**Problem**: Canvas cleared without your action

**Possible Causes**:
- Room owner cleared the canvas
- Another user cleared (if permissions allow)
- Connection interrupted and canvas reloaded empty

**Note**: Canvas clear actions are broadcast to all users immediately.

---

### Performance Issues

**Problem**: Lag, stuttering, or slow response

**Solutions**:
- Close other browser tabs
- Check internet speed
- Reduce number of users in room
- Use a more powerful device
- Clear browser cache
- Try a different browser

---

## Keyboard Shortcuts

Currently, the application uses mouse/touch input only. Keyboard shortcuts may be added in future versions.

---

## Browser Compatibility

**Recommended Browsers**:
- Google Chrome (latest version)
- Mozilla Firefox (latest version)
- Microsoft Edge (latest version)
- Safari (latest version)

**Not Supported**:
- Internet Explorer
- Browsers with JavaScript disabled

---

## Security and Privacy

### Data Storage

- Passwords are securely hashed (never stored in plain text)
- Canvas data is stored in PostgreSQL database
- JWT tokens expire after 60 minutes (default)

### Best Practices

1. **Strong Passwords**: Use unique, complex passwords
2. **Logout**: Always logout when using shared computers
3. **Private Rooms**: Don't share room IDs publicly
4. **Sensitive Content**: Avoid drawing confidential information

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check browser console for error messages (F12)
2. Verify system requirements are met
3. Review [SETUP.md](./SETUP.md) for configuration details
4. Contact your system administrator
5. Report bugs on GitHub (if available)

---

## Feature Requests

To request new features:
1. Open an issue on the project's GitHub repository
2. Describe the feature and use case
3. Provide examples or mockups if possible

---

**Happy Drawing!** 🎨
```
