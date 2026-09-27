# Porcelia Equipment Loan

Odoo module for managing equipment loans, returns, overdue loans, and penalties.

## Installation

1. Copy the module to the custom addons directory.
2. Update the Apps List.
3. Install **Equipment Loan**.

### Run Tests

```bash
python odoo-bin -d First_DB -u porcelia_equipment_loan --test-enable --stop-after-init --test-tags /porcelia_equipment_loan:TestEquipmentLoan
```

## Completed

* Equipment categories and items.
* Loan workflow: Draft → Confirmed → Returned / Cancelled.
* Loan overlap validation.
* Late-return penalty calculation.
* Equipment User / Manager security.
* Overdue tracking and automated reminders.
* OWL dashboard and gauge widget.
* Unit tests for the main business rules.

## Skipped

* Features not explicitly required by the assessment.

These were skipped to keep the implementation focused on the requested scope.

## Screenshots

### Gauge Widget

<img width="1331" height="454" alt="image" src="https://github.com/user-attachments/assets/942b26f7-8148-4003-ae58-eeb325f58e9e" />


### Dashboard

<img width="1338" height="547" alt="image" src="https://github.com/user-attachments/assets/1375ce46-19b6-482f-bc70-896bbaf12695" />


