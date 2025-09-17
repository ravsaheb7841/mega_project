import os
import zipfile
import platform
import subprocess

def download_dataset():
    # Kaggle command (user must have kaggle CLI installed & configured)
    kaggle_cmd = "kaggle"       #r"C:\Users\ASUS\anaconda3\Scripts\kaggle.exe"

    dataset = "masoudnickparvar/brain-tumor-mri-dataset"

    # Save in current script directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = base_dir
    zip_path = os.path.join(out_dir, "brain-tumor-mri-dataset.zip")

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    print("⬇Downloading dataset...")
    try:
        subprocess.run(
            [kaggle_cmd, "datasets", "download", "-d", dataset, "-p", out_dir, "--unzip"],
            check=True
        )
    except Exception as e:
        print(f"Error while downloading: {e}")
        return

    extracted_folder = os.path.join(out_dir, "Brain Tumor MRI Dataset")
    if os.path.exists(extracted_folder):
        print(f"Dataset is ready at: {extracted_folder}")
        return

    if os.path.exists(zip_path):
        print("Extracting dataset manually...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(out_dir)
        os.remove(zip_path)
        print(f"Dataset download")

if __name__ == "__main__":
    download_dataset()
