import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading


API_URL = "http://127.0.0.1:8000/quotes"
selected_id = None  # 紀錄選中的資料 ID


# 更新畫面下方的狀態列，顯示目前的操作狀態
def update_status(message, color="black"):
    status_label.config(text=message, fg=color)


# 根據是否有選取資料，啟用或停用更新和刪除按鈕
def toggle_buttons_state(is_selected):
    state = tk.NORMAL if is_selected else tk.DISABLED
    btn_update.config(state=state)
    btn_delete.config(state=state)


# 清空輸入框，並重置選取的資料狀態
def clear_inputs():
    global selected_id
    selected_id = None
    txt_content.delete("1.0", tk.END)
    ent_author.delete(0, tk.END)
    ent_tags.delete(0, tk.END)
    toggle_buttons_state(False)


# 把從 API 拿到的資料顯示在表格中，並清空輸入框
def render_treeview_data(data):
    for item in tree.get_children():
        tree.delete(item)
    for quote in data:
        tags = quote.get("tags", "")
        tree.insert(
            "", "end", values=(quote["id"], quote["author"], quote["text"], tags)
        )
    clear_inputs()


# 如果 API 請求失敗，顯示錯誤訊息
def handle_api_error(error_msg):
    update_status("錯誤：無法連線至後端 API。請確認 API 是否已啟動。", "red")
    messagebox.showerror("連線錯誤", f"API 請求失敗：\n{error_msg}")


# 從 API 拿資料，並更新到畫面上
def worker_fetch_data(success_msg="資料載入完成"):
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        form.after(0, lambda: render_treeview_data(data))
        form.after(0, lambda: update_status(success_msg, "green"))
    except Exception as e:
        form.after(0, lambda: handle_api_error(str(e)))


# 把新資料傳送到 API
def worker_add_data(payload):
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        response.raise_for_status()
        worker_fetch_data(success_msg="新增成功！")
    except Exception as e:
        form.after(0, lambda: handle_api_error(str(e)))


# 更新 API 中的資料
def worker_update_data(qid, payload):
    try:
        url = f"{API_URL}/{qid}"
        response = requests.put(url, json=payload, timeout=5)
        if response.status_code == 404:
            form.after(
                0, lambda: update_status("錯誤：操作失敗，找不到目標資料。", "red")
            )
            return
        response.raise_for_status()
        worker_fetch_data(success_msg="更新成功！")
    except Exception as e:
        form.after(0, lambda: handle_api_error(str(e)))


# 刪除 API 中的資料
def worker_delete_data(qid):
    try:
        url = f"{API_URL}/{qid}"
        response = requests.delete(url, timeout=5)
        if response.status_code == 404:
            form.after(
                0, lambda: update_status("錯誤：操作失敗，找不到目標資料。", "red")
            )
            return
        response.raise_for_status()
        worker_fetch_data(success_msg="刪除成功！")
    except Exception as e:
        form.after(0, lambda: handle_api_error(str(e)))


# 點擊重新整理按鈕時，觸發資料更新
def start_refresh():
    update_status("連線中，請稍候...", "blue")
    threading.Thread(target=worker_fetch_data, daemon=True).start()


# 點擊新增按鈕時，檢查輸入內容，然後新增資料
def on_add_click():
    text = txt_content.get("1.0", tk.END).strip()
    author = ent_author.get().strip()
    tags = ent_tags.get().strip()

    if not text or not author:
        messagebox.showwarning("警告", "內容與作者為必填欄位！")
        return

    payload = {"text": text, "author": author, "tags": tags}
    update_status("連線中，請稍候...", "blue")
    threading.Thread(target=worker_add_data, args=(payload,), daemon=True).start()


# 點擊更新按鈕時，檢查輸入內容，然後更新資料
def on_update_click():
    if not selected_id:
        return
    text = txt_content.get("1.0", tk.END).strip()
    author = ent_author.get().strip()
    tags = ent_tags.get().strip()

    payload = {"text": text, "author": author, "tags": tags}
    update_status("連線中，請稍候...", "blue")
    threading.Thread(
        target=worker_update_data, args=(selected_id, payload), daemon=True
    ).start()


# 點擊刪除按鈕時，確認後刪除資料
def on_delete_click():
    if not selected_id:
        return
    if not messagebox.askyesno("確認刪除", f"確定要刪除 ID {selected_id} 嗎？"):
        return
    update_status("連線中，請稍候...", "blue")
    threading.Thread(
        target=worker_delete_data, args=(selected_id,), daemon=True
    ).start()


# 當使用者選取表格中的資料時，顯示到輸入框中
def on_tree_select(event):
    global selected_id
    selection = tree.selection()
    if not selection:
        return

    values = tree.item(selection[0], "values")
    selected_id = values[0]

    ent_author.delete(0, tk.END)
    ent_author.insert(0, values[1])
    txt_content.delete("1.0", tk.END)
    txt_content.insert("1.0", values[2])
    ent_tags.delete(0, tk.END)
    ent_tags.insert(0, values[3])

    toggle_buttons_state(True)
    update_status(f"已選取 ID: {selected_id}", "black")


# 定義畫面上的元件，包括表格、輸入框、按鈕和狀態列
# main: 主程式入口，負責建立畫面並啟動應用程式
def main():
    global form, tree, status_label, txt_content, ent_author, ent_tags, btn_update, btn_delete

    form = tk.Tk()
    form.title("名言佳句管理系統")
    form.geometry("800x650")

    # --- A. 資料顯示區 (Treeview) ---
    frame_top = tk.Frame(form)
    frame_top.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    columns = ("id", "author", "text", "tags")
    tree = ttk.Treeview(frame_top, columns=columns, show="headings")

    tree.heading("id", text="ID")
    tree.column("id", width=50, anchor="center")
    tree.heading("author", text="作者")
    tree.column("author", width=120, anchor="w")
    tree.heading("text", text="名言內容")
    tree.column("text", width=400, anchor="w")
    tree.heading("tags", text="標籤")
    tree.column("tags", width=150, anchor="w")

    sb = ttk.Scrollbar(frame_top, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # 新增/編輯區
    frame_edit = tk.LabelFrame(form, text="新增 / 編輯區", padx=10, pady=10)
    frame_edit.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(frame_edit, text="名言內容 (Text):").grid(
        row=0, column=0, sticky="nw", pady=5
    )
    txt_content = tk.Text(frame_edit, height=5, width=65)
    txt_content.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="w")

    tk.Label(frame_edit, text="作者 (Author):").grid(
        row=1, column=0, sticky="w", pady=5
    )
    ent_author = tk.Entry(frame_edit, width=25)
    ent_author.grid(row=1, column=1, sticky="w", padx=5)

    tk.Label(frame_edit, text="標籤 (Tags):").grid(row=1, column=2, sticky="w", pady=5)
    ent_tags = tk.Entry(frame_edit, width=25)
    ent_tags.grid(row=1, column=3, sticky="w", padx=5)

    # 操作選項區
    frame_btns = tk.LabelFrame(form, text="操作選項", padx=10, pady=10)
    frame_btns.pack(fill=tk.X, padx=10, pady=5)

    tk.Button(
        frame_btns, text="重新整理 (Refresh)", command=start_refresh, width=15
    ).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_btns, text="新增 (Add)", command=on_add_click, width=15).pack(
        side=tk.LEFT, padx=5
    )

    btn_update = tk.Button(
        frame_btns,
        text="更新 (Update)",
        command=on_update_click,
        width=15,
        state=tk.DISABLED,
    )
    btn_update.pack(side=tk.LEFT, padx=5)

    btn_delete = tk.Button(
        frame_btns,
        text="刪除 (Delete)",
        command=on_delete_click,
        width=15,
        state=tk.DISABLED,
    )
    btn_delete.pack(side=tk.LEFT, padx=5)

    # 狀態列 (Status Bar)
    status_label = tk.Label(form, text="準備就緒", relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(side=tk.BOTTOM, fill=tk.X)

    start_refresh()
    form.mainloop()


if __name__ == "__main__":
    main()
