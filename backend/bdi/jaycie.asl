+request(REQUEST) <-
    .process_request(REQUEST).


//!start.

//PROFESSIONALS = ["Monica","Diego"].

//intent("Something","Another something").



+!agenda(PROFESSIONAL) <-
    .check_agenda(PROFESSIONAL, RESULT_AGENDA);
    .print(RESULT_AGENDA).

+!schedule_appointment(PROFESSIONAL, CUSTOMER, SERVICE, DATE_TIME) <-
    .schedule_appointment(PROFESSIONAL, CUSTOMER, SERVICE, DATE_TIME, RESULT_APPOINTMENT);
    .print(RESULT_APPOINTMENT).


+!check_business_hours <-
    .check_business_hours(BUSINESS_HOURS);
    .print(BUSINESS_HOURS).

//+!reply_to_bot(MESSAGE) <-
//    .reply_to_bot(MESSAGE).

+!start <-
    .print("Oi, Jaycie aqui...").

//+!start <-
    //.custom_action(15, X);
    //.print("X =", X).
//    .check_professionals_by_service("pe", X);
//    .print("X = ", X).