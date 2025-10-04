$(document).ready(function () {
    function updateMarketData() {
        $.ajax({
            url: "/api/market_data",
            type: "GET",
            dataType: "json",
            success: function (data) {
                if (data.error) {
                    console.error(data.error);
                    return;
                }

                // Update commodities
                $('#gold-price').text(data.GOLD || 'N/A');
                $('#silver-price').text(data.SILVER || 'N/A');
                $('#oil-price').text(data.CRUDE_OIL || 'N/A');

                // Update stocks
                if (Object.keys(data.stocks).length > 0) {
                    $('#no-stocks-msg').hide();
                }

                for (const ticker in data.stocks) {
                    const price = data.stocks[ticker];
                    $(`li[data-ticker="${ticker}"] .badge`).text(price);
                }
            },
            error: function (xhr, status, error) {
                console.error("Failed to fetch market data:", error);
            }
        });
    }

    // Initial call
    updateMarketData();

    // Update every 2 minutes
    setInterval(updateMarketData, 120000);
});