module com.widget.schedule {
    requires javafx.controls;
    requires javafx.fxml;
    requires com.fasterxml.jackson.databind;

    opens com.widget.schedule to javafx.fxml, com.fasterxml.jackson.databind;
    exports com.widget.schedule;
}