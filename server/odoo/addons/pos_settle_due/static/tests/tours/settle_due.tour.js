/** @odoo-module */
import * as PartnerListScreenPoS from "@point_of_sale/../tests/tours/helpers/PartnerListScreenTourMethods";
import * as PartnerListScreenSettleDue from "@pos_settle_due/../tests/helpers/PartnerListScreenTourMethods";
const PartnerListScreen = { ...PartnerListScreenPoS, ...PartnerListScreenSettleDue };
import * as ProductScreen from "@point_of_sale/../tests/tours/helpers/ProductScreenTourMethods";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("SettleDueButtonPresent", {
    test: true,
    steps: () =>
        [
            ProductScreen.clickPartnerButton(),
            PartnerListScreen.clickPartnerDetailsButton("A Partner"),
            PartnerListScreen.settleButtonTextIs("Deposit money"),
            PartnerListScreen.clickBack(),
            ProductScreen.clickPartnerButton(),
            PartnerListScreen.clickPartnerDetailsButton("B Partner"),
            PartnerListScreen.settleButtonTextIs("Settle due accounts"),
        ].flat(),
});
