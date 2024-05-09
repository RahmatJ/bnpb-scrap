import calendar
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


def handleRow(row):
    kib_col = row.find_elements(By.TAG_NAME,"td")[1]
    provinsi = kib_col.find_elements(By.TAG_NAME,"span")[0].text
    kota = kib_col.find_elements(By.TAG_NAME,"span")[1].text
    bencana = kib_col.find_elements(By.TAG_NAME,"span")[2].text
    tahun = kib_col.find_elements(By.TAG_NAME,"span")[3].text
    bulan = kib_col.find_elements(By.TAG_NAME,"span")[4].text
    tanggal = kib_col.find_elements(By.TAG_NAME,"span")[5].text
    index = kib_col.find_elements(By.TAG_NAME,"span")[6].text
    wilayah = row.find_elements(By.TAG_NAME,"td")[2].text
    kejadian = row.find_elements(By.TAG_NAME,"td")[3].text
    return {
        "kib":{
            "provinsi": provinsi,
            "kota": kota,
            "bencana": bencana,
            "tahun": tahun,
            "bulan": bulan,
            "tanggal": tanggal,
            "index": index
        },
        "wilayah": wilayah,
        "kejadian":kejadian
    }

def access_table_page(driver):
    data = []
    # accessing table data
    table = driver.find_element(By.CSS_SELECTOR, "#mytabel")
    body = table.find_element(By.CSS_SELECTOR, "#mytabel > tbody")
    rows = body.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        row_data = handleRow(row=row)
        data.append(row_data)

    return data

def write_output(result, year):
    result_json = json.dumps(result, indent=4)
    current_timestamp = calendar.timegm(time.gmtime())
    file_name = "output/{year}-{timestamp}.json".format(year=year, timestamp=current_timestamp)
    with open(file_name, "w") as outfile:
        print("writing result...")
        outfile.write(result_json)
    
    print('Output written!')

def get_yearly_data(driver, selected_year):
    print("Get data from {year}...".format(year=selected_year))
    
    # Waiting year dropdown to shown
    WebDriverWait(driver=driver,timeout=10).until(EC.presence_of_element_located((By.ID, "th")))

    # Select selected_year from dropdown
    tahun_dd = Select(driver.find_element(By.ID, "th"))
    tahun_dd.select_by_visible_text(selected_year)

    # waiting for reload
    WebDriverWait(driver=driver,timeout=10).until(EC.presence_of_element_located((By.ID, "th")))
    tahun_dd = Select(driver.find_element(By.ID, "th"))
    th_dd_text = tahun_dd.first_selected_option.text

    # make sure year selected correctly
    assert selected_year == th_dd_text, "Wrong year"

    hasNext = True
    result = []

    while hasNext:
        # locating table
        WebDriverWait(driver=driver,timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mytabel")))
        data = access_table_page(driver=driver)
        result.extend(data)

        paginations = driver.find_element(By.CLASS_NAME,"pagination")
        fast_forward_btns = paginations.find_elements(By.CLASS_NAME, "fa-forward")

        hasNext = False
        if(len(fast_forward_btns) > 0):
            hasNext = True

        if(hasNext):
            print("clicking item")
            fast_forward_btns[0].click()

    write_output(result=result, year=selected_year)


def main():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options)
    driver.get("https://dibi.bnpb.go.id/xdibi2")

    years = ["2021","2022"]

    for year in years:
        get_yearly_data(driver=driver, selected_year=year)
    
    print('finished scrapping!. Closing driver...')
    driver.quit()
    print('driver closed!')


if __name__ == "__main__":
    main()
