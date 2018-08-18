

$(function() {

    Morris.Area({
        element: 'morris-area-chart',
        data: [{
            quizDateTime: '2012-02-17 08:00:00',
            percentage: 37,

        }, {
            quizDateTime: '2012-02-18 09:00:00',
            percentage: 52,

        }, {
            quizDateTime: '2012-02-21 10:00:00',
            percentage: 100,

        }, {
            quizDateTime: '2012-02-22 15:00:00',
            percentage: 70,

        }, {
            quizDateTime: '2012-02-25 19:00:00',
            percentage: 23,

        }],
        xkey: ['quizDateTime'],
        ykeys: ['percentage'],
        labels: ['percentage'],
        pointSize: 2,
        hideHover: 'auto',
        resize: true
    });

    Morris.Donut({
        element: 'morris-donut-chart',
        data: [{
            label: "Download Sales",
            value: 12
        }, {
            label: "In-Store Sales",
            value: 30
        }, {
            label: "Mail-Order Sales",
            value: 20
        }],
        resize: true
    });

    Morris.Bar({
        element: 'morris-bar-chart',
        data: [{
            y: '2006',
            a: 100,
            b: 90
        }, {
            y: '2007',
            a: 75,
            b: 65
        }, {
            y: '2008',
            a: 50,
            b: 40
        }, {
            y: '2009',
            a: 75,
            b: 65
        }, {
            y: '2',
            a: 50,
            b: 40
        }, {
            y: '3',
            a: 75,
            b: 65
        }, {
            y: '4',
            a: 100,
            b: 90
        }],
        xkey: 'y',
        ykeys: ['a', 'b'],
        labels: ['Series A', 'Series B'],
        hideHover: 'auto',
        resize: true
    });

});
