# PayamResan

SMS sending module for [payam-resan.com](https://payam-resan.com)
![Downloads](https://static.pepy.tech/personalized-badge/payamresan?period=total&units=international_system&left_color=black&right_color=green&left_text=Downloads)


---

## 📦 Installation

```bash
pip install payamresan
````

---

## 🚀 Quick Usage

```python
from payamresan import Payamak

payam = Payamak(api_key="YOUR_API_KEY", sender="YOUR_SENDER_NUMBER")

payam.send_sms("Hello!", "+989123456789")
```

---

## ✅ Checking for Success or Error

You can store the result of `send_sms()` in a variable and check its status:

```python
result = payam.send_sms("Hello!", "+989123456789")

if result["Success"] == True:
    print("✅ Message sent successfully!")
else:
    print("❌ Error:", result["ErrorCode"])
```

---

## 💡 Notes

* Make sure your API key and sender number are active on [payam-resan.com](https://payam-resan.com).
* You can send to multiple recipients:

  ```python
  payam.send_sms("Hello everyone!", "+989111111111", "+989122222222", "+989133333333")
  ```

---

## 🧑‍💻 Author

Ali – [GitHub](https://github.com/yourusername)
