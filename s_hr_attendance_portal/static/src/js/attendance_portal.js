odoo.define("s_hr_attendance_portal.register_attendance", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    const Dialog = require("web.Dialog");
    const { _t, qweb } = require("web.core");
    const session = require("web.session");
    var field_utils = require("web.field_utils");

    publicWidget.registry.PortalRegisterAttendance = publicWidget.Widget.extend(
        {
            selector: ".o_portal_attendance_register",
            events: {
                "click .o_attendance_sign_in_btn": _.debounce(
                    function () {
                        this.update_attendance();
                    },
                    200,
                    true
                ),
                "click .o_attendance_sign_out_btn": _.debounce(
                    function () {
                        this.update_attendance();
                    },
                    200,
                    true
                ),
                "click .o_attendance_sign_in_dismiss_btn": _.debounce(
                    function () {
                        clearTimeout(this.attendance_sign_in_dismiss_timer);
                        $(".o_portal_attendance_register .o_attendance_main").removeClass("d-none");
                        $(".o_portal_attendance_register .oe_attendance_sign_in_msg").addClass("d-none");

                    },
                    200,
                    true
                ),
                "click .o_attendance_sign_out_dismiss_btn": _.debounce(
                    function () {
                        clearTimeout(this.attendance_sign_out_dismiss_timer)
                        $(".o_portal_attendance_register .o_attendance_main").removeClass("d-none");
                        $(".o_portal_attendance_register .o_attendance_sign_out_msg").addClass("d-none");
                    },
                    200,
                    true
                ),
            },
            start: function () {
                var self = this;
                return this._super.apply(this, arguments).then(function () {
                    self.employee_id = self.$el.data("uid");
                    self.hours_today = self.$el.data("hours_today");
                    self.start_clock();
                    return Promise.resolve();
                });
            },
            destroy: function () {
                clearInterval(this.clock_start);
                this._super.apply(this, arguments);
            },
            start_clock: function () {
                /**
                 * Actualizar el tiempo trabajado, cada un minuto sumarlo
                 */
                var self = this;
                this.clock_start = setInterval(function () {
                    self.hours_today = self.hours_today + 1 / 60;
                    var hour_number = field_utils.format.float_time(
                        self.hours_today
                    );
                    $(".o_attendance_sign_out .o_hours_number").html(
                        hour_number
                    );
                }, 60000);
            },
            update_attendance: function () {
                var self = this;
                this._rpc({
                    model: "res.users",
                    method: "portal_attendance_action",
                    args: [self.employee_id],
                    context: session.user_context,
                }).then(function (result) {
                    self.hours_today = result["hours_today"];
                    self.update_attendance_view(result);
                });
            },
            update_attendance_view: function (result) {
                var attendance = result["attendance"];
                if (!attendance["check_out"]) {
                    // ckecked in
                    $(".o_portal_attendance_register .o_attendance_sign_in").addClass("d-none");
                    $(".o_portal_attendance_register .o_attendance_sign_out").removeClass("d-none");
                    var hour_number = field_utils.format.float_time(
                        result["hours_today"]
                    );
                    $(".o_attendance_sign_out .o_hours_number").html(
                        hour_number
                    );
                    $(".o_portal_attendance_register .o_attendance_sign_in_time").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));
                    $(".o_portal_attendance_register .o_attendance_main").addClass("d-none");
                    $(".o_portal_attendance_register .oe_attendance_sign_in_msg").removeClass("d-none");
                    this.attendance_sign_in_dismiss_timer = setTimeout(() => {
                        $(".o_portal_attendance_register .o_attendance_main").removeClass("d-none");
                        $(".o_portal_attendance_register .oe_attendance_sign_in_msg").addClass("d-none");
                    }, 5000);
                } else {
                    // ckecked out
                    $(".o_portal_attendance_register .o_attendance_sign_in").removeClass("d-none");
                    $(".o_portal_attendance_register .o_attendance_sign_out").addClass("d-none");

                    $(".o_portal_attendance_register .o_attendance_sign_out_time").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));
                    $(".o_portal_attendance_register .o_attendance_main").addClass("d-none");
                    $(".o_portal_attendance_register .o_attendance_sign_out_msg").removeClass("d-none");
                    this.attendance_sign_out_dismiss_timer = setTimeout(() => {
                        $(".o_portal_attendance_register .o_attendance_main").removeClass("d-none");
                        $(".o_portal_attendance_register .o_attendance_sign_out_msg").addClass("d-none");
                    }, 5000);
                }
            },
        }
    );
});
