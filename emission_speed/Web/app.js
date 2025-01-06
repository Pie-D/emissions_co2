// // Mock API (dùng tạm trong app.js)
// async function fetchEmissionData() {
//     return {
//         time: Array.from({ length: 24 }, (_, i) => i), // 0-23 giờ
//         CO: Array.from({ length: 24 }, () => (Math.random() * 0.2 + 0.1).toFixed(2)),
//         NOx: Array.from({ length: 24 }, () => (Math.random() * 0.1 + 0.05).toFixed(2)),
//         VOC: Array.from({ length: 24 }, () => (Math.random() * 0.05 + 0.01).toFixed(2)),
//         CO2: Array.from({ length: 24 }, () => (Math.random() * 50 + 100).toFixed(2))
//     };
// }
// // Fetch dữ liệu API (ví dụ với dữ liệu giả lập)
// // async function fetchEmissionData() {
// //     // Thay URL dưới đây bằng API của ngài
// //     const response = await fetch('https://example.com/api/emission');
// //     const data = await response.json();
// //     return data; // API trả về dạng: { time: [], CO: [], NOx: [], VOC: [], CO2: [] }
// // }

// // Hàm tạo biểu đồ
// async function createEmissionChart() {
//     const data = await fetchEmissionData();

//     // Dữ liệu cần hiển thị
//     const labels = data.time; // Mảng giờ (0-23)
//     const CO = data.CO;       // Carbon Monoxide (CO)
//     const NOx = data.NOx;     // Nitrogen Oxides (NOx)
//     const VOC = data.VOC;     // Volatile Organic Compounds (VOC)
//     const CO2 = data.CO2;     // Carbon Dioxide (CO2)

//     // Cấu hình biểu đồ
//     const ctx = document.getElementById('emissionChart').getContext('2d');
//     new Chart(ctx, {
//         type: 'bar',
//         data: {
//             labels: labels, // Trục X
//             datasets: [
                
//                 {
//                     label: 'CO2 (g/veh)',
//                     data: CO2,
//                     type: 'line',
//                     borderColor: 'red',
//                     borderWidth: 2,
//                     fill: false,
//                     yAxisID: 'y-axis-2'
//                 },
//                 {
//                     label: 'CO (g/veh)',
//                     data: CO,
//                     backgroundColor: 'orange',
//                     stack: 'stack1'
//                 },
//                 {
//                     label: 'NOx (g/veh)',
//                     data: NOx,
//                     backgroundColor: 'blue',
//                     stack: 'stack1'
//                 },
//                 {
//                     label: 'VOC (g/veh)',
//                     data: VOC,
//                     backgroundColor: 'yellow',
//                     stack: 'stack1'
//                 }
//             ]
//         },
//         options: {
//             responsive: true,
//             scales: {
//                 x: {
//                     stacked: true, // Xếp chồng các thanh
//                 },
//                 y: {
//                     stacked: true,
//                     title: {
//                         display: true,
//                         text: 'Pollutant Traffic Emission Intensity (g/veh)'
//                     }
//                 },
//                 'y-axis-2': {
//                     position: 'right',
//                     title: {
//                         display: true,
//                         text: 'CO2 Traffic Emission Intensity (g/veh)'
//                     },
//                     grid: {
//                         drawOnChartArea: false // Không hiển thị lưới trục phụ
//                     }
//                 }
//             },
//             plugins: {
//                 legend: {
//                     position: 'top'
//                 },
//                 tooltip: {
//                     mode: 'index',
//                     intersect: false
//                 }
//             }
//         }
//     });
// }

// Khởi tạo biểu đồ khi tải trang
// createEmissionChart();
// Hàm lấy dữ liệu từ API với tham số ngày và ID camera
async function fetchEmissionData(date, cameraId,viewType) {
    try {
        // const response = await fetch(`https://example.com/api/emission?date=${date}&cameraId=${cameraId}`);
        const response = await fetch(`http://127.0.0.1:5000/emission_day?cameraId=${cameraId}&day=${date}&viewType=${viewType}`);
        const data = await response.json();
        return data; // API trả về: { time: [], CO: [], NOx: [], VOC: [], CO2: [] }
    } catch (error) {
        console.error("Lỗi khi gọi API:", error);
        alert("Không thể tải dữ liệu. Vui lòng thử lại.");
        return null;
    }
}

// Hàm tạo biểu đồ
async function createEmissionChart(date, cameraId,viewType) {
    const data = await fetchEmissionData(date, cameraId,viewType);
    if (!data) return; // Nếu không có dữ liệu, thoát
    const unit = viewType === 'average' ? 'g/veh' : 'g';
    // Dữ liệu cần hiển thị
    const labels = data.time; // Mảng giờ (0-23)
    // const CO = data.CO;       // Carbon Monoxide (CO)
    // const NOx = data.NOx;     // Nitrogen Oxides (NOx)
    // const VOC = data.VOC;     // Volatile Organic Compounds (VOC)
    // const CO2 = data.CO2;     // Carbon Dioxide (CO2)

    // Hủy biểu đồ cũ (nếu có)
    if (window.emissionChart instanceof Chart) {
        window.emissionChart.destroy();
    }

    // Tạo biểu đồ mới
    const ctx = document.getElementById('emissionChart').getContext('2d');
    window.emissionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: `CO2 (${unit})`,
                    data: data.CO2,
                    type: 'line',
                    borderColor: 'red',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    yAxisID: 'y-axis-2'
                },
                {
                    label: `CO (${unit})`,
                    data: data.CO,
                    backgroundColor: 'orange',
                    stack: 'stack1'
                },
                {
                    label: `NOx (${unit})`,
                    data: data.NOx,
                    backgroundColor: 'blue',
                    stack: 'stack1'
                },
                {
                    label: `VOC (${unit})`,
                    data: data.VOC,
                    backgroundColor: 'yellow',
                    stack: 'stack1'
                }
            ]
        },
        options: {
            responsive: true,
            // maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true // Xếp chồng các thanh
                },
                y: {
                    stacked: true, // Xếp chồng các khí CO, NOx, VOC
                    title: {
                        display: true,
                        text: `Pollutant Traffic Emission Intensity (${unit})`
                    }
                },
                'y-axis-2': {
                    position: 'right', // Đặt trục phụ bên phải
                    title: {
                        display: true,
                        text: `CO2 Traffic Emission Intensity (${unit})`
                    },
                    grid: {
                        drawOnChartArea: false // Không vẽ lưới trên diện tích biểu đồ
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top' // Đặt chú giải ở trên
                },
                tooltip: {
                    mode: 'index', // Hiển thị dữ liệu của tất cả dataset khi rê chuột
                    intersect: false
                }
            }
        }        
    });
}

// Lắng nghe sự kiện submit form
document.getElementById('filterForm').addEventListener('submit', async (event) => {
    event.preventDefault(); // Ngăn trình duyệt tải lại trang

    // Lấy giá trị từ input
    const date = document.getElementById('date').value;
    const cameraId = document.getElementById('cameraId').value;
    const viewType = document.getElementById('viewType').value;

    // Gọi hàm tạo biểu đồ với tham số
    await createEmissionChart(date, cameraId, viewType);
});

// Khởi tạo mặc định với giá trị hôm nay và camera ID 1
// const today = new Date().toISOString().split('T')[0];
p1 = document.getElementById('date').value = '2024-12-14';
p2 = document.getElementById('cameraId').value = 16;
p3 = document.getElementById('viewType').value = 'average';
// document.getElementById('chartTitle').textContent = 'Traffic Emission Intensity ${today} camera id: 1';
createEmissionChart(p1,p2,p3);
