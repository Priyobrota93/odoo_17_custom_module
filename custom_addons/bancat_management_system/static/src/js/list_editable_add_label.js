odoo.define('bancat_management_system.ListEditableAddLabel', function (require) {
    'use strict';

    const ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        _renderFooter: function () {
            const $footer = this._super.apply(this, arguments);

            // Check the model name or arch to set a specific label
            if (this.state.model === 'bancat.patient.file') {
                // Change "Add a line" to "Add a file" for patient file model
                $footer.find('.o_add_row').text('Add a file');
            } else if (this.state.model === 'bancat.attendance') {
                // Change "Add a line" to "Add an attendance" for attendance model
                $footer.find('.o_add_row').text('Add attendances');
            }

            return $footer;
        },
    });
});