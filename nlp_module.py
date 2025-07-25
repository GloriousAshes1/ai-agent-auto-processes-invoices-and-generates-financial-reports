import re


def preprocess(lines):
    return [line.strip() for line in lines if line.strip()]


def parse_price(value: str):
    try:
        return float(
            value.replace(',', '').replace('RM', '').replace('VND', '').replace('T', '').replace('$', '').replace('%',
                                                                                                                  '').strip())
    except:
        return None


def is_valid_product_line(line):
    line_lower = line.lower()
    # Reject blacklisted keywords
    if any(k in line_lower for k in
           ['jalan', 'room', 'location', 'pos', 'cashier', 'no:', 'fax', 'tel', 'sp:', 'mb:', 'gst', 'tax', 'vat',
            'change', 'rounding', 'total']):
        return False
    # Must contain some letters
    if not any(c.isalpha() for c in line):
        return False
    # Must contain a number (price)
    if not re.search(r"[\d.,]{2,}", line):
        return False
    return True


def is_numeric_only_line(line):
    line = line.replace('-', '').replace('%', '')
    return bool(re.fullmatch(r"[0-9.,]+", line.strip()))


def extract_fields(lines: list[str]):
    result = {
        "company_name": None,
        "invoice_date": None,
        "total_amount": None,
        "vat_amount": None,
        "payment_method": None,
        "products": []
    }

    # 1. Company Name
    for i in range(5):
        line = lines[i]
        if line.upper() not in ["RECEIPT", "INVOICE"] and any(c.isalpha() for c in line):
            result["company_name"] = line.strip().lower()
            break

    # 2. Invoice Date
    for line in lines:
        match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", line)
        if match:
            result["invoice_date"] = match.group(1)
            break

    # 3. VAT Amount
    for line in lines:
        if any(k in line.lower() for k in ['vat', 'tax', 'gst']):
            prices = re.findall(r"[-]?\d[\d.,]*", line)
            if prices:
                vat = parse_price(prices[-1])
                if vat is not None and vat >= 0:
                    result["vat_amount"] = vat
                    break

    # 4. Total Amount – dòng gần cuối, ưu tiên có chữ "total"
    for line in reversed(lines[-10:]):
        if any(k in line.lower() for k in ["total", "amount due", "grand total", "tổng cộng"]):
            prices = re.findall(r"[\d.,]+", line)
            for p in reversed(prices):
                amt = parse_price(p)
                if amt and amt > 0:
                    result["total_amount"] = amt
                    break
        if result["total_amount"]:
            break

    # 5. Payment method
    for line in lines:
        if "visa" in line.lower():
            result["payment_method"] = "VISA"
            break
        elif "cash" in line.lower():
            result["payment_method"] = "CASH"
            break
        elif "master" in line.lower():
            result["payment_method"] = "MASTERCARD"
            break
    if not result["payment_method"]:
        result["payment_method"] = "UNKNOWN"

    # 6. Product lines
    for line in lines:
        if is_numeric_only_line(line):
            continue  # bỏ dòng chỉ có số

        if not is_valid_product_line(line):
            continue

        prices = re.findall(r"[\d.,]+", line)
        if prices:
            price = parse_price(prices[-1])
            if price and price < 1_000_000:
                result["products"].append({
                    "name": line.strip(),
                    "qty": 1,
                    "price": price
                })

    return result


def nlp_module(ocr_text: str) -> dict:
    lines = preprocess(ocr_text.split("\n"))
    fields = extract_fields(lines)

    # Check required fields
    # required_fields = ['company_name', 'invoice_date', 'total_amount', 'vat_amount', 'payment_method']
    # missing = [k for k in required_fields if not fields.get(k)]
    # if missing:
    #     raise ValueError(f"❌ Missing required fields: {missing}")
    return fields
