import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QRadioButton, QTextEdit, QListWidgetItem, QListWidget, QProgressBar
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.uic import loadUi
from urllib.parse import quote

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('YouTube Search & Hospital Search.ui', self)
        
        self.radio_neck = self.findChild(QRadioButton, 'radio_neck')
        self.radio_shoulder = self.findChild(QRadioButton, 'radio_shoulder')
        self.radio_back = self.findChild(QRadioButton, 'radio_back')
        self.radio_knee = self.findChild(QRadioButton, 'radio_knee')
        self.radio_upper_back = self.findChild(QRadioButton, 'radio_upper_back')
        self.radio_wrist = self.findChild(QRadioButton, 'radio_wrist')
        self.radio_ankle = self.findChild(QRadioButton, 'radio_ankle')
        self.web_engine_view = self.findChild(QWebEngineView, 'web_engine_view')
        self.address_line_edit = self.findChild(QLineEdit, 'address_line_edit')
        self.search_button = self.findChild(QPushButton, 'search_button')
        self.result_list_widget = self.findChild(QListWidget, 'result_list_widget')
        self.details_text_edit = self.findChild(QTextEdit, 'details_text_edit')
        self.progress_bar = self.findChild(QProgressBar, 'progress_bar')
        
        self.links = {
            '목': 'https://youtube.com/shorts/0i7kJodD4ws?si=7kVoehH3rYr9RLSs',
            '어깨': 'https://youtu.be/PfERed6LRmQ?si=zrGGF1wd_FakqOSU',
            '허리': 'https://youtu.be/Ju5_WR8VxRI?si=JHRIHmBsQ_NU8Xcd',
            '무릎': 'https://youtu.be/3dB4R3a2Pi4?si=dfeF7XlbTy7I1TCi',
            '등': 'https://youtu.be/ya86wAsM5Xk?si=DV4K8vi-3bSiu0gX',
            '손목': 'https://youtu.be/At2RJXtYJKk?si=XMwLbv8D_8cTSVeD',
            '발목': 'https://youtu.be/WEaCwo2peFc?si=XGRNyOIvghHUzyqO'
        }

        self.radio_neck.toggled.connect(self.change_link)
        self.radio_shoulder.toggled.connect(self.change_link)
        self.radio_back.toggled.connect(self.change_link)
        self.radio_knee.toggled.connect(self.change_link)
        self.radio_upper_back.toggled.connect(self.change_link)
        self.radio_wrist.toggled.connect(self.change_link)
        self.radio_ankle.toggled.connect(self.change_link)
        
        self.search_button.clicked.connect(self.search_hospitals)
        self.result_list_widget.itemClicked.connect(self.show_place_details)
        
        self.api_key = 'AIzaSyArVa1Tg_FqURhYfGFAc4iF6_hhyoeYCo0'
        self.max_results = 5  
    
    def change_link(self):
        url = ''
        if self.radio_neck.isChecked():
            url = self.links['목']
        elif self.radio_shoulder.isChecked():
            url = self.links['어깨']
        elif self.radio_back.isChecked():
            url = self.links['허리']
        elif self.radio_knee.isChecked():
            url = self.links['무릎']
        elif self.radio_upper_back.isChecked():
            url = self.links['등']
        elif self.radio_wrist.isChecked():
            url = self.links['손목']
        elif self.radio_ankle.isChecked():
            url = self.links['발목']

        if url:
            self.web_engine_view.setUrl(QUrl(url))
        else:
            self.web_engine_view.setUrl(QUrl('about:blank'))

    def search_hospitals(self):
        address = self.address_line_edit.text()
        
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={self.api_key}'
        
        self.progress_bar.setRange(0, 0) 
        QApplication.processEvents() 
        
        response = requests.get(geocode_url)
        if response.status_code != 200:
            print('Error fetching geocode data')
            self.progress_bar.reset()
            return
        
        geocode_data = response.json()
        if not geocode_data['results']:
            print('No results found for the given address')
            self.progress_bar.reset()
            return
        
        location = geocode_data['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        
        places_url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&rankby=distance&type=hospital&keyword=정형외과&key={self.api_key}'
        
        response = requests.get(places_url)
        if response.status_code != 200:
            print('Error fetching places data')
            self.progress_bar.reset()
            return
        
        places_data = response.json()
        self.result_list_widget.clear()
        count = 0
        for place in places_data['results']:
            if count >= self.max_results:
                break
            name = place['name']
            address = place.get('vicinity', 'No address provided')
            item = QListWidgetItem(f'{name}\n{address}', self.result_list_widget)
            item.setData(Qt.UserRole, place['place_id'])
            count += 1
        
        self.progress_bar.reset()
    
    def show_place_details(self, item):
        place_id = item.data(Qt.UserRole)
        
        details_url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={self.api_key}'
        
        self.progress_bar.setRange(0, 0)
        QApplication.processEvents() 
        
        response = requests.get(details_url)
        if response.status_code != 200:
            print('Error fetching place details')
            self.progress_bar.reset()
            return
        
        details_data = response.json()
        if 'result' not in details_data:
            print('No details found for the selected place')
            self.progress_bar.reset()
            return
        
        result = details_data['result']
        name = result.get('name', 'N/A')
        address = result.get('formatted_address', 'N/A')
        phone = result.get('formatted_phone_number', 'N/A')
        rating = result.get('rating', 'N/A')
        hours = result.get('opening_hours', {}).get('weekday_text', [])
        
        details = f'Name: {name}\nAddress: {address}\nPhone: {phone}\nRating: {rating}\n\nHours:\n'
        details += '\n'.join(hours) if hours else 'No hours available'
        
        self.details_text_edit.setText(details)
        
        self.progress_bar.reset()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
