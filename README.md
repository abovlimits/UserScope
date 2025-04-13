# UserScope
This script, `main.py`, is a powerful username search tool designed to locate the presence of a given username across numerous social media platforms. It leverages concurrent requests for efficient searches and provides real-time results.

## 🚀 Features
- 🔍 Search for usernames across a vast array of social media platforms.
- ⚡ Multithreaded support for faster and more efficient searches.
- 💾 Option to save results to a file for future reference.
- 🛠️ Customizable timeout and thread count for flexible usage.

## 📋 Requirements
Ensure you have the following installed:
- Python 3.x
- `requests` library
- `pyfiglet` library
- `colorama` library
- `argparse` (standard library)

## 🛠️ Installation
1. Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2. Navigate to the project directory:
    ```bash
    cd UserScope
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## 🖥️ Usage
Run the script with:
```bash
python main.py
```

### 🔧 Optional Arguments
- `-t`, `--threads`: Specify the number of threads to use (default: 10).
- `--timeout`: Set the timeout for requests in seconds (default: 10).
- `-o`, `--output`: Provide a file path to save the results.

### 💡 Example
To search for a username with custom settings:
```bash
python main.py -t 20 --timeout 15 -o results.txt
```

## 📜 License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🤝 Contributing
Contributions are welcome! Feel free to submit a pull request or open an issue for any improvements or bug fixes.

## 📞 Support
If you encounter any issues or have questions, please open an issue in the repository.

---
Happy searching! 🎉
