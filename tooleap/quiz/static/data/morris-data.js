$(function() {

    Morris.Area({
        element: 'morris-area-chart',
        data: [{
            period: '2010 Q1',
            tax: 3,
            import: 5,
            export: 3
        }, {
            period: '2010 Q2',
            tax: 4,
            import: 4,
            export: 4
        }, {
            period: '2010 Q3',
            tax: 6,
            import: 7,
            export: 8
        }, {
            period: '2010 Q4',
            tax: 12,
            import: 3,
            export: 2
        }, {
            period: '2011 Q1',
            tax: 5,
            import: 7,
            export: 4
        }, {
            period: '2011 Q2',
            tax: 6,
            import: 4,
            export: 3
        }, {
            period: '2011 Q3',
            tax: 7,
            import: 6,
            export: 11
        }, {
            period: '2011 Q4',
            tax: 12,
            import: 2,
            export: 3
        }, {
            period: '2012 Q1',
            tax: 5,
            import: 2,
            export: 34
        }, {
            period: '2012 Q2',
            tax: 23,
            import: 3,
            export: 1
        }],
        xkey: 'period',
        ykeys: ['tax', 'import', 'export'],
        labels: ['tax', 'import', 'export'],
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
            y: '2010',
            a: 50,
            b: 40
        }, {
            y: '2011',
            a: 75,
            b: 65
        }, {
            y: '2012',
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
