// Storage doughnut chart
let tests_ctx = document.getElementById('storage-chart-area').getContext('2d');
let tests_config = {
    type: 'doughnut',
    data: {
        datasets: [{
            data: [
                $('#used_storage_space').val(),
                $('#allotted_storage_space').val()
            ],
            backgroundColor: [
                '#EC0B43',
                '#0B4F6C',
            ],
            label: 'Dataset 1'
        }],
        labels: [
            'Used storage space (in GB)',
            'Total storage space (in GB)'
        ]
    },
    options: {
        maintainAspectRatio: false,
        legend: {
            position: 'top',
        },
        title: {
            display: true,
            fontColor: '#0B4F6C',
            fontSize: 23,
            text: 'Storage stats for your account'
        },
        animation: {
            animateScale: true,
            animateRotate: true
        }
    }
};

myDoughnut = new Chart(tests_ctx, tests_config);

// Assignments doughnut chart
let ctx = document.getElementById('assignments-chart-area').getContext('2d');
let config = {
    type: 'doughnut',
    data: {
        datasets: [{
            data: [
                $('#number_of_submitted_assignments').val(),
                $('#total_number_of_assignments').val()
            ],
            backgroundColor: [
                '#EC0B43',
                '#0B4F6C',
            ],
            label: 'Dataset 1'
        }],
        labels: [
            'Submitted assignments',
            'Total assignments'
        ]
    },
    options: {
        maintainAspectRatio: false,
        legend: {
            position: 'top',
        },
        title: {
            display: true,
            fontColor: '#0B4F6C',
            fontSize: 23,
            text: 'See how students are performing'
        },
        animation: {
            animateScale: true,
            animateRotate: true
        }
    }
};

myDoughnut = new Chart(ctx, config);
