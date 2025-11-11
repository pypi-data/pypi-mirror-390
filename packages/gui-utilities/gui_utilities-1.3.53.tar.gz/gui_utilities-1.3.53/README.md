# GUI Utilities

Personal use library with utilities for building stylish and reusable PyQt6 UI components.

/----------------------------------------------------------------------------------------------------/

## Features

/----------------------------------------------------------------------------------------------------/

### UI Components

- create_window(): creates a base window already configured with layout and initial styles.

- create_label(): creates customized labels.

- create_button(): creates customized buttons.

- create_text_box(): creates customized text boxes.

- create_combo_box(): creates customized drop-down lists.

- create_information_message_box(): creates customized information dialog boxes.

- create_confirmation_message_box(): creates customized confirmation dialog boxes.

- confirm_exit(): creates a confirmation dialog box to exit the application.

/----------------------------------------------------------------------------------------------------/

### Window & Layout Control

- switch_instance(): dynamically switches the content of the main window's "central_widget".

- get_responsive_width(): calculates a responsive width based on screen size to maintain an adaptive UI.

/----------------------------------------------------------------------------------------------------/

### Input Validation

- validate_string(): checks that the input is not empty.

- validate_integer(): checks that the input contains only integer numbers (supports European numeric formatting).

- validate_id(): checks that the input is an Argentinian D.N.I. (supports European numeric formatting).

- validate_cellphone_number(): checks Argentinian cellphone numbers with ten digits.

- validate_email(): checks emails using an updated list of domains (TLDs) from IANA or local cache.

/----------------------------------------------------------------------------------------------------/

#### TLDs management (E-mail validation)

- get_tlds(): obtains an updated list of TLDs from IANA; if it fails, uses the local list.

- export_tlds(): saves the list of TLDs locally for offline use.

- import_tlds(): loads the locally saved TLDs if internet access is unavailable.

- build_email_pattern(): dynamically generates the regular expression that validates emails using TLDs.

/----------------------------------------------------------------------------------------------------/

### Formatting helpers

- decimal_format(): applies European number formatting.

- format_id(): applies correct formatting to Argentinian D.N.I.'s according to length using European number formatting.

- cellphone_number_format(): applies correct formatting to Argentinian cellphone numbers.

/----------------------------------------------------------------------------------------------------/

## Installation

pip install gui_utilities