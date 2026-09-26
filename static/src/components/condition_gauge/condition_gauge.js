/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class ConditionGauge extends Component {
    static template = "porcelia_equipment_loan.ConditionGauge";

    static props = {
        ...standardFieldProps,
        segments: { type: Number, optional: true },
    };

    static extractProps({ options }) {
        return {
            segments: options?.segments || 10,
        };
    }

    get value() {
        return this.props.record.data[this.props.name] || 0;
    }

    get segments() {
        return Array.from(
            { length: this.props.segments },
            (_, index) => index + 1
        );
    }

    get filledSegments() {
        return Math.round(
            (this.value / 100) * this.props.segments
        );
    }

    getSegmentClass(segment) {
        if (segment > this.filledSegments) {
            return "condition-gauge-segment";
        }

        if (this.value < 40) {
            return "condition-gauge-segment red";
        }

        if (this.value < 75) {
            return "condition-gauge-segment amber";
        }

        return "condition-gauge-segment green";
    }

    setValue(event) {
        if (this.props.readonly) {
            return;
        }

        const segment = parseInt(
            event.currentTarget.dataset.segment
        );

        const value = Math.round(
            (segment / this.props.segments) * 100
        );

        this.props.record.update({
            [this.props.name]: value,
        });
    }
}

const conditionGaugeField = {
    component: ConditionGauge,
    supportedTypes: ["integer"],
    extractProps: ConditionGauge.extractProps,
};

registry.category("fields").add(
    "condition_gauge",
    conditionGaugeField
);