from robot.api import logger
import Browser
from RPA.Robocorp.Vault import Vault
from RPA.Tables import Tables
from RPA.Crypto import Hash
from RPA.Crypto import Crypto
from RPA.PDF import PDF
from RPA.Archive import Archive
# TODO install dialog prerequists
from RPA.Dialogs import Dialogs


class AuditSite:
    def __init__(self, site: str):
        self.site = site

    def load_order_list(self):
        logger.info("Gleich mal laden")
        _secret = Vault().get_secret("orderdata")
        tables = Tables()
        crypto =  Crypto()
        with open(_secret["csvhash"]) as f:
            csv_data = f.read()
        assert crypto.hash_string(csv_data, method=Hash.SHA3_224) == _secret["csvhash"]
        # TODO Eliminate race condition vulnerability of reading csv-file twice from disk.

        self.orderlist = tables.read_table_from_csv(
            path = _secret["csvhash"],
            header = True,
            columns = ["Order number","Head","Body","Legs","Address"], 
            dialect="unix", 
            delimiters=",", 
            encoding="ascii"
            )
        self.orderlist = tables.export_table(self.orderlist, False, True)
        logger.info("Geladen")

    def start_browser(self):
        self.browser = Browser.Browser()
        self.browser.new_browser(browser=Browser.SupportedBrowsers.chromium)
        # self.browser.new_browser(browser=Browser.SupportedBrowsers.chromium,
        #     headless=False
        #     )
        self.browser_id_1 = self.browser.new_context(javaScriptEnabled=True)
        self.browser_id_2 = self.browser.new_context(javaScriptEnabled=False)
    
    def validate_page_script(self):
        # TODO find other sources of dynamic content and audit.
        # TODO implement checksum comparison
        def validate_script(self):
            elements = self.browser.get_elements("css=script")
            assert len(elements) == 3
            for i in range(3):
                with open("./audited-" + str(i) + ".js") as f:
                    audited = f.read()
                    if i == 0:
                        script = self.browser.get_property(elements[i], "innerText")
                        assert audited == script
                    else:
                        js = self.browser.download(self.browser.get_property(elements[i], "src"))
                        with open(js["saveAs"]) as f:
                            assert f.read() == audited
        self.browser.switch_context(self.browser_id_2)
        self.browser.new_page(self.site)
        validate_script(self)
        self.browser.close_context(self.browser_id_2)
        self.browser.switch_context(self.browser_id_1)
        self.browser.new_page(self.site)
        validate_script(self)

    def current_order(self):
        current_line = self.orderlist.pop()
        self.ordernumber = current_line["Order number"]
        self.head = current_line["Head"]
        self.body = current_line["Body"]
        self.leg = current_line["Legs"]
        self.address = current_line["Address"]

    def give_up_all_constitutional_rights(self):
        self.ensure_constitutional_rights()
        self.browser.click(selector="text=OK")
        self.validate_constitutional_rights()

    def ensure_constitutional_rights(self):
        # TODO Implement proper Error handling and Logging
        assert "block" == self.browser.get_style("css=.modal", "display")
    
    def validate_constitutional_rights(self):
        # TODO Implement proper Error handling and Logging
        assert "none" == self.browser.get_style("css=.modal", "display")

    def enter_data(self):
        self.ensure_data()
        self.browser.select_options_by("id=head", Browser.SelectAttribute.value, self.head)
        self.browser.check_checkbox(selector="id=id-body-" + self.body)
        self.browser.fill_text(selector="css=:not(input#address).form-control",  txt=self.leg)
        self.browser.fill_text(selector="css=input#address",  txt=self.address)
        self.validate_data()

    def ensure_data(self):
        assert "" == self.browser.get_selected_options("id=head", Browser.SelectAttribute.value)
        # assert True == self.browser.get_ch  get_checkbox_state("id=id-body-" + self.body)
        for i in range(1,7):
            assert False == self.browser.get_checkbox_state("id=id-body-" + str(i))
        assert "" == self.browser.get_text(selector="css=:not(input#address).form-control")
        assert "" == self.browser.get_text(selector="css=input#address")

    def validate_data(self):
        # TODO Implement proper Error handling and Logging
        assert self.head == self.browser.get_selected_options("id=head", Browser.SelectAttribute.value)
        assert True == self.browser.get_checkbox_state("id=id-body-" + self.body)
        assert self.leg == self.browser.get_text(selector="css=:not(input#address).form-control")
        assert self.address == self.browser.get_text(selector="css=input#address")

    def preview_robot(self):
        self.ensure_robot()
        self.browser.click(selector="id=preview")
        self.validate_robot()
        self.browser.take_screenshot(filename=self.ordernumber, selector="id=robot-preview-image", disableAnimations=True)

    def ensure_robot(self):
        # TODO Implement proper Error handling and Logging
        assert 0 == self.browser.get_element_count("id=robot-preview-image") 

    def validate_robot(self):
        # TODO Implement proper Error handling and Logging
        assert 1 == self.browser.get_element_count("id=robot-preview-image") 
        logger.info(f"Current Order: {self.ordernumber}")
        logger.info(self.browser.get_element_states("css=#robot-preview-image > div"))
        logger.info(self.browser.get_element_states("css=#robot-preview-image div"))
        
    def submit_order(self):
        self.ensure_order()
        self.browser.click(selector="id=order")
        self.validate_order()
    
    def ensure_order(self):
        assert 1 == self.browser.get_element_count(selector="id=order")
        # TODO Implement proper Error handling and Logging
    
    def validate_order(self):
        try:
            assert "attached" in self.browser.get_element_states("id=order-another")
        except AssertionError:
            logger.warn("Order Button does not work this time.")
            # TODO install dialog prerequists
            dialog = Dialogs()
            dialog.add_heading("Order Button does not work this time.")
            dialog.add_submit_buttons("OK")
            dialog.run_dialog()
            self.submit_order()
        # TODO Implement proper Error handling and Logging

    def start_another_order(self):
        self.ensure_another_order()
        self.browser.click("id=order-another")
        self.validate_another_order()

    def ensure_another_order(self):
        assert 1 == self.browser.get_element_count("id=parts")
        # TODO Implement proper Error handling and Logging

    def validate_another_order(self):
        assert 0 == self.browser.get_element_count("id=parts")
        # TODO Implement proper Error handling and Logging

    def validate_order_input(self):
        self.timestamp = self.browser.get_text("css=h3 + div")
        logger.info(self.timestamp.replace(":","").replace(".","").replace("-","").isalnum())
        assert self.timestamp.replace(":","").replace(".","").replace("-","").isalnum()

        self.badge_success = self.browser.get_text("css=.badge-success")
        logger.info(len(self.badge_success[15:]) < 11)
        logger.info(self.badge_success)
        assert "RSB-ROBO-ORDER-" in self.badge_success
        assert len(self.badge_success[15:]) < 12
        assert self.badge_success[15:].isalnum()

        self.head_to_check = self.browser.get_text("css=#parts > div:nth-of-type(1)")
        assert self.head_to_check == "Head: " + self.head

        self.body_to_check = self.browser.get_text("css=#parts > div:nth-of-type(2)")
        assert self.body_to_check == "Body: " + self.body

        self.leg_to_check = self.browser.get_text("css=#parts > div:nth-of-type(3)")
        assert self.leg_to_check == "Legs: " + self.leg

        self.address_to_check = self.browser.get_text("css=h3 ~ p:nth-of-type(2)")
        assert self.address_to_check == self.address

    def batch_submit_order(self):
        self.load_order_list()
        self.start_browser()
        logger.info("Startet Browser mit der Seite: " + self.site)
        self.validate_page_script()

        for _ in range(len(self.orderlist)):
            self.current_order()
            self.give_up_all_constitutional_rights()
            self.enter_data()
            self.preview_robot()
            self.submit_order()
            self.validate_order_input()
            self.generate_pdf()
            self.start_another_order()
            
        self.finalize()

    def finalize(self):
        # TODO Implement proper Error handling and Logging
        # TODO Clean up data
        self.browser.close_browser()
        self.archive_pdfs()

    ###########################################

    def generate_pdf(self):
        pdf = PDF()
        cur_data = {"robopic": f"output/browser/screenshot/{self.ordernumber}.png", "orderid": self.badge_success, "head": self.head, "body": self.body, "leg": self.leg, "address": self.address, "timestamp": self.timestamp}
        pdf.template_html_to_pdf("template.html", f"pdf/{self.ordernumber}.pdf", cur_data)
        # TODO find another place for pdf init.
    
    def archive_pdfs(self):
        lib = Archive()
        lib.archive_folder_with_zip("pdf", "output/archive.zip")
        