
# App lọc và tắt tiếng video theo từ khóa

## Giới thiệu
Ứng dụng này cho phép người dùng tải lên các tập tin âm thanh hoặc video, và lọc hoặc tắt tiếng các từ khóa cụ thể trong đoạn phát. Điều này hữu ích trong việc quản lý nội dung âm thanh cho các mục đích khác nhau như chỉnh sửa video, quyền riêng tư, hoặc thậm chí là kiểm duyệt.

## Công nghệ Sử Dụng
- ![Whisper](https://img.shields.io/badge/Whisper-OpenAI-blue) Một mô hình nhận dạng giọng nói của OpenAI, được sử dụng để chuyển đổi âm thanh thành văn bản và xác định vị trí của từng từ trong âm thanh.
- ![Python](https://img.shields.io/badge/Python-3.8+-blue.svg) Ngôn ngữ lập trình chính cho việc phát triển ứng dụng.
- ![FFmpeg](https://img.shields.io/badge/FFmpeg-Libraries-red.svg) Thư viện xử lý media mạnh mẽ, được sử dụng để xử lý các tệp âm thanh và video.
- ![Pydub](https://img.shields.io/badge/Pydub-Audio%20Handling-green) Thư viện Python giúp dễ dàng xử lý các tác vụ âm thanh.
- ![Librosa](https://img.shields.io/badge/Librosa-Audio%20Analysis-orange) Thư viện Python cho phép tải và phân tích tín hiệu âm thanh.
- ![Tkinter](https://img.shields.io/badge/Tkinter-GUI%20Framework-purple) Giao diện người dùng đồ họa cho Python, được sử dụng để xây dựng giao diện của ứng dụng.
- ![CUDA](https://img.shields.io/badge/CUDA-NVIDIA-green) Cần thiết để tận dụng khả năng của GPU cho các mô hình như Whisper.

## Cách Hoạt Động
1. **Tải Âm Thanh/Video**: Người dùng tải lên tập tin âm thanh hoặc video mà họ muốn xử lý.
2. **Chọn Mô Hình**: Người dùng chọn một mô hình Whisper tương ứng với nhu cầu VRAM và độ chính xác mong muốn.
3. **Xử Lý Âm Thanh**: Âm thanh được phân tích, với từng từ được nhận dạng và thời gian bắt đầu/kết thúc được xác định.
4. **Tắt Tiếng Từ Khóa**: Các từ khóa được người dùng nhập vào sẽ được tắt tiếng trong đoạn phát.
5. **Lưu Kết Quả**: Âm thanh đã được xử lý có thể được lưu lại dưới dạng tệp âm thanh hoặc được gắn vào video gốc và lưu dưới dạng tệp video mới.

## Cài Đặt
Để chạy ứng dụng, cần cài đặt các thư viện sau:
```
pip install whisper pydub librosa soundfile sounddevice GPUtil ffmpeg-python
```
Đảm bảo rằng bạn đã cài đặt [CUDA](https://developer.nvidia.com/cuda-downloads) để sử dụng GPU.

## Chạy Ứng Dụng
Để chạy ứng dụng, sử dụng lệnh sau từ thư mục chứa tệp app.py:
```
python app.py
```
## Lưu Ý
Ứng dụng này yêu cầu truy cập vào GPU với đủ VRAM để tải và chạy các mô hình Whisper lớn. Hãy đảm bảo rằng hệ thống của bạn đáp ứng các yêu cầu này trước khi cố gắng tải một mô hình lớn.
