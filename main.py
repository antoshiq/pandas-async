import pandas as pd
import functions as pf
import asyncio
import time

file_path = 'medical_diagnostic_devices_10000.xlsx'

# синхронно
def run_synchronous():
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"Файла {file_path} не существует")
        return None

    df = pf.date_normalize(df)
    df = pf.status_normalize(df)
    df = pf.invalid_calibration_date_normalize(df)

    with pd.ExcelWriter('medical_devices_report_sync.xlsx') as writer:
        pf.get_active_warranty(df).to_excel(writer, sheet_name='Active_Warranty', index=False)
        pf.get_clinics_with_most_issues(df).to_excel(writer, sheet_name='Issues_by_Clinic', index=False)
        pf.get_needs_calibration_models(df).to_excel(writer, sheet_name='Calibration_Report', index=False)
        pf.create_pivot_table(df).to_excel(writer, sheet_name='Pivot_Summary')


# асинхронно

# вспомогательные функции для асинхронного выполнения так как
# по заданию выполненные действия необходимо записать в РАЗНЫЕ файлы асинхронно
def save_to_excel(df, filename, sheet_name, index=False):
    with pd.ExcelWriter(filename) as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=index)

async def save_to_excel_async(df, filename, sheet_name, index=False):
    await asyncio.to_thread(save_to_excel, df, filename, sheet_name, index)


async def run_asynchronous():
    try:
        # асинронное чтение файла
        df = await asyncio.to_thread(pd.read_excel, file_path)
    except FileNotFoundError:
        print(f"Файла {file_path} не существует")
        return None

    df = pf.date_normalize(df)
    df = pf.status_normalize(df)
    df = pf.invalid_calibration_date_normalize(df)

    # асинхронно формируем отчеты
    task_warranty = asyncio.to_thread(pf.get_active_warranty, df)
    task_issues = asyncio.to_thread(pf.get_clinics_with_most_issues, df)
    task_calibration = asyncio.to_thread(pf.get_needs_calibration_models, df)
    task_pivot = asyncio.to_thread(pf.create_pivot_table, df)

    # ждем выполнения всех расчетов параллельно
    df_warranty, df_issues, df_calibration, df_pivot = await asyncio.gather(
        task_warranty, task_issues, task_calibration, task_pivot
    )

    # асинхронная запись в РАЗНЫЕ файлы 
    await asyncio.gather(
        save_to_excel_async(df_warranty, 'report_active_warranty.xlsx', 'Active_Warranty', index=False),
        save_to_excel_async(df_issues, 'report_issues_by_clinic.xlsx', 'Issues_by_Clinic', index=False),
        save_to_excel_async(df_calibration, 'report_calibration.xlsx', 'Calibration_Report', index=False),
        save_to_excel_async(df_pivot, 'report_pivot_summary.xlsx', 'Pivot_Summary', index=True)
    )


# сравнение времени
async def main():
    print("замер времени")

    # 1. синхронный
    start_sync = time.time()
    run_synchronous()
    end_sync = time.time()
    sync_duration = end_sync - start_sync
    print(f"Синхронное выполнение: {sync_duration:.4f} сек.")

    # 2. асинхронный
    start_async = time.time()
    await run_asynchronous()
    end_async = time.time()
    async_duration = end_async - start_async
    print(f"Асинхронное выполнение: {async_duration:.4f} сек.")

    # 3. сравнение
    print("\n\n")
    if sync_duration > async_duration:
        diff = sync_duration - async_duration
        
        print(f"Результат: Асинхронный код быстрее на {diff:.4f} сек.")
    else:
        diff = async_duration - sync_duration
        print(f"Результат: Синхронный код оказался быстрее на {diff:.4f} сек.")



if __name__ == "__main__":
    asyncio.run(main())