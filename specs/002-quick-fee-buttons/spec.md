# Feature Specification: Quick Fee Amount Buttons

**Feature Branch**: `002-quick-fee-buttons`  
**Created**: 2026-04-04  
**Status**: Draft  
**Input**: User description: " http://localhost:3001/pos there is fees section, we want to make a some buttons like 10, 30, 50, 100, and each fee type so it will be fast to access seamlessly, these buttons we can modify it in settings"

## Clarifications

### Session 2026-04-05

- Q: How should preset configurations be uniquely identified and scoped? → A: Presets are uniquely identified by fee type and store location, stored as separate setting keys for each location
- Q: What user roles or permissions control who can configure vs use preset amounts? → A: Any authenticated user with system role "Manager" or higher can configure presets, all POS operators can use them
- Q: What should the system display when no preset amounts are configured for a fee type? → A: Show no preset buttons and display placeholder text "Configure presets in settings"
- Q: Should there be a maximum limit on the number of preset amounts per fee type? → A: Maximum of 8 presets per fee type, prevents UI clutter while allowing sufficient variety
- Q: How should preset amount buttons be ordered when displayed in the POS interface? → A: Display in ascending numerical order (smallest to largest)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Apply Common Fee Amounts Quickly (Priority: P1)

As a POS operator, I need to quickly add common fee amounts to transactions without manual typing, so I can process sales faster and reduce errors in fee entry.

**Why this priority**: This is the core value proposition - reducing time and errors in fee entry during transaction processing, which directly impacts checkout speed and operational efficiency.

**Independent Test**: Can be fully tested by adding a fee in the POS interface using a quick-amount button and verifying the correct amount is applied without manual input, delivering immediate time savings.

**Acceptance Scenarios**:

1. **Given** I am processing a transaction with shipping fees, **When** I click the "10" quick-amount button in the shipping fee section, **Then** the fee value field automatically populates with $10 (or equivalent currency)
2. **Given** I am adding a custom fee, **When** I select a quick-amount button, **Then** the amount appears in the fee value field immediately without requiring keyboard input
3. **Given** I have multiple fee types to add, **When** I use quick-amount buttons for each fee type sequentially, **Then** each fee is added correctly with the selected amount

---

### User Story 2 - Configure Quick Amount Presets (Priority: P2)

As a store administrator, I need to customize which quick-amount buttons appear for each fee type in the POS interface, so I can tailor the system to my business's most common fee scenarios.

**Why this priority**: After the basic functionality works, customization allows businesses to optimize for their specific workflow, increasing the feature's value and adoption.

**Independent Test**: Can be fully tested by accessing settings, modifying quick-amount presets for a fee type, returning to POS, and verifying the new preset buttons appear and function correctly, delivering personalized checkout experience.

**Acceptance Scenarios**:

1. **Given** I am in the settings interface, **When** I add preset amount "25" for shipping fees, **Then** the POS interface displays a "25" quick-amount button in the shipping fee section
2. **Given** I have configured preset amounts [10, 30, 50, 100] for shipping fees, **When** I modify them to [15, 25, 75], **Then** only the new presets [15, 25, 75] appear as buttons in the POS interface
3. **Given** I want different presets for different fee types, **When** I configure [10, 30, 50] for shipping and [20, 40, 60] for installation, **Then** each fee type section shows its specific preset buttons

---

### User Story 3 - Override Preset with Custom Input (Priority: P3)

As aPOS operator, I need to manually enter a different amount even after clicking a quick-amount button, so I can handle unique fee situations that don't match my presets.

**Why this priority**: While less common, this ensures flexibility and prevents operators from being locked into preset amounts when exceptions occur.

**Independent Test**: Can be fully tested by clicking a quick-amount button, then manually editing the amount field to a different value, and verifying both the visual state and the final submitted amount, delivering flexibility for edge cases.

**Acceptance Scenarios**:

1. **Given** I clicked the "30" quick-amount button for shipping, **When** I manually change the value to "35", **Then** the field accepts "35" and the transaction processes with the custom $35 shipping fee
2. **Given** I have a preset amount selected, **When** I clear the field and type a new value, **Then** the custom value takes precedence over the preset
3. **Given** I need to add multiple fees of the same type with different amounts, **When** I use presets for most but manually enter exceptions, **Then** all fees are recorded correctly in the transaction

---

### Edge Cases

- When a user configures zero preset amounts for a fee type, the system displays no quick-amount buttons and shows placeholder text "Configure presets in settings" to guide users
- When a user attempts to configure more than 8 presets, the system rejects the configuration and displays an error message indicating the maximum limit
- How does the system behave when preset amounts exceed typical transaction values? (No technical restriction, may want guidance in settings UI)
- What happens when two fee types have conflicting preset configurations? (Each fee type maintains independent preset configuration)
- How does the system handle negative amounts entered in settings? (Settings should validate and reject negative preset values)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display quick-amount buttons in the fees section of the POS interface for each configured fee type
- **FR-002**: System MUST allow users to click a quick-amount button to populate the fee value field with the corresponding amount
- **FR-003**: System MUST provide a settings interface where administrators can configure preset amount options for each fee type
- **FR-004**: System MUST persist preset amount configurations across sessions and users
- **FR-005**: System MUST allow users to manually edit the fee value field after clicking a quick-amount button
- **FR-006**: System MUST support independent preset configurations for each fee type (shipping, installation, custom)
- **FR-007**: System MUST validate preset amounts to prevent negative values during configuration
- **FR-008**: System MUST limit preset configuration to a maximum of 8 preset amounts per fee type
- **FR-009**: System MUST display presets in ascending numerical order (smallest to largest) regardless of configuration order
- **FR-010**: System MUST restrict preset configuration to users with "Manager" role or higher, while allowing all POS operators to use the quick-amount buttons
- **FR-011**: System MUST apply the quick-amount to the currently selected fee when the button is clicked
- **FR-012**: System MUST display quick-amount buttons only for amounts that are configured in settings
- **FR-013**: System MUST display placeholder text "Configure presets in settings" when no preset amounts are configured for a fee type
- **FR-014**: System MUST update the POS interface immediately when preset configurations change in settings

### Key Entities

- **Fee Type Preset Configuration**: Represents the collection of quick-amount buttons for a specific fee type and store location. Uniquely identified by the combination of fee type identifier (shipping/installation/custom) and store location ID. Includes list of preset amounts (maximum 8 per fee type). Presets are automatically sorted and displayed in ascending numerical order (smallest to largest) in the POS interface. Stored as separate setting keys per location, preventing accidental cross-location preset sharing.

- **Fee Transaction Entry**: Represents a single fee added to a transaction. Includes fee type, label, amount (which may have been set via quick-amount button or manual entry), and calculation method (fixed/percentage). Already exists in current system.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operators can add a common fee using quick-amount buttons in under 2 seconds, compared to 5-8 seconds for manual entry
- **SC-002**: 80% of fee entries use quick-amount buttons instead of manual input once presets are configured for common scenarios
- **SC-003**: Fee entry errors (incorrect decimal placement, typos) decrease by 50% for transactions using quick-amount buttons
- **SC-004**: Administrators can configure or modify fee presets in under 1 minute without technical assistance
- **SC-005**: The POS interface loads and displays quick-amount buttons within 200ms of accessing the fees section, maintaining current performance standards
- **SC-006**: 90% of users successfully complete a fee addition using quick-amount buttons on their first attempt after brief familiarization

## Assumptions

- Users have basic familiarity with the existing POS interface and fee addition process
- The current fee types (shipping, installation, custom) will remain the same; new fee types added in future will require preset configuration
- Each business location maintains its own preset configurations (not shared across locations)
- Preset amounts are stored in the default currency of the system
- Users with "Manager" role or higher have permissions to access settings and modify fee preset configurations; all POS operators can use existing presets
- Quick-amount buttons apply to fixed-amount fees; percentage-based fees continue to use manual input
- The existing settings system (key-value storage) will be extended to store preset configurations
- Operators can distinguish between quick-amount buttons for different fee types visually (labels, positioning, or color coding)
- Default preset amounts (10, 30, 50, 100) will be provided for each fee type upon initial system setup, editable by administrators