// Đặt tất cả mã trong một IIFE (Immediately Invoked Function Expression)
(function ($) {
    // Định nghĩa hàm updateTotals
    function updateTotals() {
        console.log("updateTotals function called");
        let totalRoto = 0;
        let totalPaint = 0;
        let totalTrack = 0;
        let totalComp = 0;
        let totalShots = 0;
        let rotoShots = 0;
        let paintShots = 0;
        let trackShots = 0;
        let compShots = 0;

        $('#shot-table tbody tr').each(function () {
            const shotNameInput = $(this).find('input[name$="-shot_name"]');
            const shotName = shotNameInput.length ? shotNameInput.val().trim() : '';
            const roto = parseFloat($(this).find('input[name$="-md_roto"]').val()) || 0;
            const paint = parseFloat($(this).find('input[name$="-md_paint"]').val()) || 0;
            const track = parseFloat($(this).find('input[name$="-md_track"]').val()) || 0;
            const comp = parseFloat($(this).find('input[name$="-md_comp"]').val()) || 0;

            if (shotName) {
                totalShots++;
                if (roto > 0) rotoShots++;
                if (paint > 0) paintShots++;
                if (track > 0) trackShots++;
                if (comp > 0) compShots++;
            }

            totalRoto += roto;
            totalPaint += paint;
            totalTrack += track;
            totalComp += comp;

            console.log("Row values:", { shotName, roto, paint, track, comp });
        });

        console.log("Totals calculated:", { totalRoto, totalPaint, totalTrack, totalComp, totalShots, rotoShots, paintShots, trackShots, compShots });

        $('#total-shots').text(totalShots);
        updateMDSummary('roto', rotoShots, totalRoto);
        updateMDSummary('paint', paintShots, totalPaint);
        updateMDSummary('track', trackShots, totalTrack);
        updateMDSummary('comp', compShots, totalComp);
    }

    function updateMDSummary(type, shots, total) {
        console.log(`Updating ${type} summary: ${shots} shots, ${total} MD`);
        const summaryElement = $(`.${type}-summary`);
        if (total > 0) {
            $(`#${type}-shots`).text(shots);
            $(`#total-${type}`).text(total.toFixed(2));
            summaryElement.show();
            console.log(`${type} summary shown`);
        } else {
            summaryElement.hide();
            console.log(`${type} summary hidden`);
        }
    }

    function updateTotalIfPositive(elementId, value) {
        console.log(`Updating ${elementId} with value ${value}`);
        const element = $('#' + elementId);
        const parentElement = element.closest('.summary-item');
        if (value > 0) {
            element.text(value.toFixed(2));
            parentElement.show();
            console.log(`${elementId} is visible with value ${value.toFixed(2)}`);
        } else {
            parentElement.hide();
            console.log(`${elementId} is hidden`);
        }
    }

    // Thêm hàm debounce ở đây
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Tạo phiên bản debounced của updateTotals
    const debouncedUpdateTotals = debounce(updateTotals, 100);

    // Định nghĩa hàm cloneMore
    function cloneMore(selector, type) {
        console.log("cloneMore function called");
        var newElement = $(selector).clone(true);
        var total = $('#id_' + type + '-TOTAL_FORMS').val();
        newElement.find(':input:not([type=button]):not([type=submit]):not([type=reset])').each(function () {
            var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
            var id = 'id_' + name;
            $(this).attr({ 'name': name, 'id': id }).val('').removeAttr('checked');
        });
        newElement.find('label').each(function () {
            var forValue = $(this).attr('for');
            if (forValue) {
                $(this).attr({ 'for': forValue.replace('-' + (total - 1) + '-', '-' + total + '-') });
            }
        });
        total++;
        $('#id_' + type + '-TOTAL_FORMS').val(total);
        $(selector).after(newElement);

        // Gọi updateTotals sau khi thêm hàng mới
        updateTotals();
    }

    // Đặt tất cả các event listeners trong document.ready
    $(document).ready(function () {
        console.log("Document ready");
        // Gọi updateTotals khi trang được load
        updateTotals();

        // Sử dụng event delegation cho cả sự kiện input và paste
        $('#shot-table').on('input paste', 'input[name$="-md_roto"], input[name$="-md_paint"], input[name$="-md_track"], input[name$="-md_comp"]', function (e) {
            console.log(e.type + " event triggered");
            debouncedUpdateTotals();  // Sử dụng phiên bản debounced
        });

        // Cập nhật tổng số khi xóa một hàng
        $(document).on('click', '.delete-row', function () {
            console.log("Row deleted");
            $(this).closest('tr').remove();
            debouncedUpdateTotals();  // Sử dụng phiên bản debounced
        });

        // Thêm sự kiện cho nút thêm hàng mới (nếu có)
        $('#add-row').on('click', function () {
            console.log("Add row clicked");
            cloneMore('tr:last', 'form');
            debouncedUpdateTotals();  // Sử dụng phiên bản debounced
        });

        // Thêm MutationObserver để theo dõi thay đổi trong bảng
        const tableObserver = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.type === 'childList' || mutation.type === 'subtree') {
                    console.log("Table content changed");
                    debouncedUpdateTotals();  // Sử dụng phiên bản debounced
                }
            });
        });

        const config = { childList: true, subtree: true };
        const targetNode = document.getElementById('shot-table');
        tableObserver.observe(targetNode, config);

        // // Thêm nút Refresh Totals để cập nhật thủ công
        // $('<button>')
        //     .text('Refresh Totals')
        //     .addClass('bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-4')
        //     .on('click', function () {
        //         console.log("Refresh totals clicked");
        //         updateTotals();  // Ở đây chúng ta có thể sử dụng updateTotals trực tiếp
        //     })
        //     .insertAfter('#shot-table');
    });

    // Đặt hàm cloneMore vào global scope nếu cần thiết
    window.cloneMore = cloneMore;

})(jQuery);  // Truyền jQuery vào IIFE để đảm bảo $ là jQuery
