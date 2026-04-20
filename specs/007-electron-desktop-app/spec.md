# Feature Specification: Convert EZOO POS to Offline Windows Desktop Application

**Feature Branch**: `007-electron-desktop-app`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: User description: "Convert EZOO POS into a fully offline Windows desktop application. Wrap the existing FastAPI backend and Next.js frontend inside Electron."

## Clarifications

### Session 2026-04-19

- Q: How should existing users migrate their data from the web/PostgreSQL version to the desktop app? → A: No migration - fresh start (suitable for new installations)
- Q: What level of logging and diagnostic information should be available for troubleshooting? → A: Local log files with built-in GUI log viewer

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install and Launch Desktop Application (Priority: P1)

As a user, I want to install the EZOO POS desktop application on Windows and launch it so that I can use the POS system without an internet connection.

**Why this priority**: This is the fundamental capability that enables all other functionality. Without a working installation and launch, nothing else matters.

**Independent Test**: Can be tested by downloading the .exe installer, running it on a fresh Windows machine, and verifying the application starts and displays the main interface.

**Acceptance Scenarios**:

1. **Given** a Windows machine with no prior EZOO POS installation, **When** I run the installer and complete installation, **Then** the application appears in the Start menu and Desktop shortcut is available.
2. **Given** the application is installed, **When** I launch it, **Then** the loading screen appears and transitions to the main POS interface within 60 seconds.
3. **Given** the application is running, **When** I close it using the window close button, **Then** all processes terminate cleanly and the system returns to its prior state.

---

### User Story 2 - Operate POS System Offline (Priority: P1)

As a user, I want to use all POS system features (products, inventory, sales, reports) without an internet connection.

**Why this priority**: The core value proposition is offline operation. All existing web functionality must work identically in the desktop app.

**Independent Test**: Can be tested by disconnecting all network adapters, then performing typical POS operations: adding products to cart, processing a sale, checking inventory, generating reports.

**Acceptance Scenarios**:

1. **Given** the application is running with no network, **When** I process a sale, **Then** the transaction completes successfully and is saved locally.
2. **Given** the application is running with no network, **When** I view inventory levels, **Then** all current stock data is displayed accurately.
3. **Given** the application is running with no network, **When** I generate a sales report, **Then** the report includes all transactions up to the current date.

---

### User Story 3 - Stable Startup and Shutdown (Priority: P2)

As a user, I want the application to start reliably every time and shut down cleanly without leaving orphaned processes.

**Why this priority**: Reliability is critical for retail environments where the POS must be ready at opening and must not cause system issues at closing.

**Independent Test**: Can be tested by starting and stopping the application 10 times consecutively, verifying no zombie processes remain and startup time is consistent.

**Acceptance Scenarios**:

1. **Given** a successful prior session, **When** I restart the application, **Then** it starts within 60 seconds without requiring any manual intervention.
2. **Given** the application is running, **When** I close it, **Then** no orphaned backend or frontend processes remain in Task Manager.
3. **Given** the application crashed unexpectedly, **When** I relaunch it, **Then** it starts successfully without file lock errors.

---

### User Story 4 - Error Recovery (Priority: P2)

As a user, I want clear feedback when something goes wrong and the ability to recover without reinstalling.

**Why this priority**: Users must be able to diagnose and resolve common issues without technical support.

**Independent Test**: Can be tested by simulating failure conditions (killing processes, blocking ports) and verifying appropriate error messages and recovery options appear.

**Acceptance Scenarios**:

1. **Given** the backend process fails to start, **When** I launch the application, **Then** an error screen explains the issue and offers a retry option.
2. **Given** the frontend process fails to start, **When** I launch the application, **Then** an error screen explains the issue and offers a retry option.
3. **Given** an error screen is displayed, **When** I click retry, **Then** the application attempts to restart the failed component.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a Windows .exe installer that can be distributed and installed without internet
- **FR-002**: System MUST start the backend service automatically when the application launches
- **FR-003**: System MUST start the frontend service automatically after the backend is ready
- **FR-004**: System MUST verify backend is responding on port 8000 before starting frontend
- **FR-005**: System MUST verify frontend is responding on port 3000 before displaying the main window
- **FR-006**: System MUST terminate all child processes when the user closes the application window
- **FR-007**: System MUST store all data in a local database (SQLite) that requires no external database server
- **FR-008**: System MUST display a loading screen while services are starting
- **FR-009**: System MUST display an error screen if backend fails to start, with retry option
- **FR-010**: System MUST display an error screen if frontend fails to start, with retry option
- **FR-011**: System MUST run in fullscreen or maximized mode by default
- **FR-012**: System MUST disable developer tools in the production build
- **FR-013**: System MUST package both frontend build and backend code into the installer
- **FR-014**: System MUST provide a built-in log viewer in the application for troubleshooting

### Key Entities *(include if feature involves data)*

- **Desktop Application Bundle**: The complete packaged application including installer, executable, and bundled services
- **Process Manager**: Component responsible for starting, monitoring, and stopping backend and frontend processes
- **Local Database**: SQLite database containing all POS data (products, inventory, transactions, settings)
- **Loading Screen**: Initial UI displayed while services start
- **Error Screen**: UI displayed when service startup fails with recovery options

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete installation and launch the application in under 5 minutes on a standard Windows PC
- **SC-002**: Application starts and displays the main POS interface within 60 seconds of launch
- **SC-003**: All core POS features (sales, inventory, products, reports) function identically to the web version when offline
- **SC-004**: No orphaned processes remain after closing the application (verified via Task Manager)
- **SC-005**: 100% of startups complete successfully over 20 consecutive launch cycles
- **SC-006**: Error recovery succeeds in restarting failed services without requiring full reinstall

## Assumptions

- Target users have Windows 10 or Windows 11 installed
- Users have local administrator rights to install the application
- The application will be distributed as a single .exe installer file
- Existing database schema will be adapted for SQLite without schema changes
- Existing PostgreSQL data will NOT be migrated - fresh local database on first install
- No changes are required to the existing FastAPI backend code
- No changes are required to the existing Next.js frontend code
- The desktop app targets the same feature set as the current web application