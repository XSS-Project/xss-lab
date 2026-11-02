"""Fixed fictional documents. IDs are stable integration keys, not list indexes."""

DOCUMENTS = (
    {
        "id": 1,
        "title": "Bắt đầu với ứng dụng Web",
        "category": "Web",
        "description": "Từ một địa chỉ trên trình duyệt đến một trang web được hiển thị.",
        "content": "Ứng dụng Web trao đổi dữ liệu giữa trình duyệt và máy chủ. Trình duyệt gửi yêu cầu; máy chủ xử lý và trả phản hồi.\n\nTrong lab này, Flask xử lý route và Jinja2 tạo HTML từ template. Dữ liệu tài liệu là dữ liệu mẫu cố định để nhóm cùng thực hành.",
    },
    {
        "id": 2,
        "title": "HTTP: request và response",
        "category": "HTTP",
        "description": "Làm quen với phương thức, đường dẫn và mã trạng thái HTTP.",
        "content": "Một HTTP request có phương thức và đường dẫn. GET dùng để đọc tài nguyên; POST thường dùng khi gửi dữ liệu để xử lý.\n\nPhản hồi 200 biểu thị yêu cầu thành công, 404 là không tìm thấy tài nguyên, 405 là phương thức không được hỗ trợ. Quan sát status cùng nội dung phản hồi khi kiểm thử.",
    },
    {
        "id": 3,
        "title": "JavaScript và cây DOM",
        "category": "JavaScript",
        "description": "Hiểu cách JavaScript đọc và cập nhật nội dung trên trang.",
        "content": "DOM biểu diễn tài liệu HTML dưới dạng cây. JavaScript có thể chọn phần tử và cập nhật nội dung hoặc thuộc tính của chúng.\n\nKhi cần hiển thị văn bản thuần, textContent giữ nội dung dưới dạng văn bản. Việc phân biệt văn bản và HTML sẽ được nghiên cứu ở module DOM-based XSS sau này.",
    },
    {
        "id": 4,
        "title": "Dữ liệu đầu vào và ranh giới tin cậy",
        "category": "An toàn ứng dụng",
        "description": "Theo dõi dữ liệu từ người dùng tới nơi ứng dụng sử dụng nó.",
        "content": "Dữ liệu từ URL, biểu mẫu hoặc bản ghi lưu trữ cần được xử lý phù hợp tại nơi sử dụng. Kiểm tra định dạng và giới hạn độ dài giúp bảo đảm yêu cầu nghiệp vụ.\n\nKhi đưa dữ liệu ra HTML, cần xử lý đầu ra theo đúng ngữ cảnh. Giới hạn độ dài không thay thế việc xử lý đầu ra. Các thí nghiệm cụ thể được dành cho giai đoạn tiếp theo.",
    },
    {
        "id": 5,
        "title": "Template Jinja2 và hiển thị văn bản",
        "category": "Web",
        "description": "Tách giao diện khỏi xử lý và giữ dữ liệu ở đúng ngữ cảnh.",
        "content": "Template dùng layout chung để các trang có cùng điều hướng và cấu trúc. Các trang con kế thừa base.html và bổ sung nội dung qua các block.\n\nJinja2 tự escape dữ liệu trong template HTML của Flask. Ví dụ ký tự < và > trong dữ liệu cần xuất hiện như văn bản thay vì trở thành thẻ ngoài ý muốn.",
    },
    {
        "id": 6,
        "title": "Query parameter và URL fragment",
        "category": "HTTP",
        "description": "Phân biệt phần truy vấn gửi tới máy chủ và fragment của trình duyệt.",
        "content": "Query parameter đứng sau dấu ? trong URL và được gửi trong request tới máy chủ. Trang tài liệu dùng category để lọc danh mục.\n\nFragment đứng sau dấu # và không được gửi trong HTTP request. Module preview sẽ sử dụng fragment ở giai đoạn DOM-based XSS; khung hiện tại chưa xử lý ghi chú.",
    },
)

CATEGORIES = tuple(sorted({document["category"] for document in DOCUMENTS}))


def get_document(document_id):
    return next((item for item in DOCUMENTS if item["id"] == document_id), None)
