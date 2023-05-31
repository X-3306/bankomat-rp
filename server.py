import socket
import json

from config import SERVER_IP, SERVER_PORT, BANK_ACCOUNTS_FILE, TRANSACTION_HISTORY_FILE

# Funkcja obsługująca żądanie wypłaty środków z konta
def withdraw_amount(account_number, amount):
    # Sprawdź poprawność danych wejściowych
    if not account_exists(account_number):
        return {'status': 'error', 'message': 'Konto nie istnieje'}
    if amount <= 0:
        return {'status': 'error', 'message': 'Nieprawidłowa kwota'}
    if not has_sufficient_balance(account_number, amount):
        return {'status': 'error', 'message': 'Niewystarczające saldo'}

    # Logika wypłaty środków z konta
    # Zaktualizuj saldo konta
    update_account_balance(account_number, -amount)
    # Dodaj wpis do historii transakcji
    add_transaction_to_history(account_number, 'Wypłata', amount)

    return {'status': 'success', 'message': f'Wypłacono {amount} jednostek waluty'}

# Funkcja obsługująca żądanie wpłaty środków na konto
def deposit_amount(account_number, amount):
    # Sprawdź poprawność danych wejściowych
    if not account_exists(account_number):
        return {'status': 'error', 'message': 'Konto nie istnieje'}
    if amount <= 0:
        return {'status': 'error', 'message': 'Nieprawidłowa kwota'}

    # Logika wpłaty środków na konto
    # Zaktualizuj saldo konta
    update_account_balance(account_number, amount)
    # Dodaj wpis do historii transakcji
    add_transaction_to_history(account_number, 'Wpłata', amount)

    return {'status': 'success', 'message': f'Wpłacono {amount} jednostek waluty'}

# Funkcja obsługująca żądanie sprawdzenia salda konta
def check_balance(account_number):
    # Sprawdź poprawność danych wejściowych
    if not account_exists(account_number):
        return {'status': 'error', 'message': 'Konto nie istnieje'}

    # Logika sprawdzania salda konta
    balance = get_account_balance(account_number)

    return {'status': 'success', 'message': f'Saldo konta: {balance}'}

# Funkcja obsługująca żądanie zmiany PIN-u
def change_pin(account_number, old_pin, new_pin):
    # Sprawdź poprawność danych wejściowych
    if not account_exists(account_number):
        return {'status': 'error', 'message': 'Konto nie istnieje'}
    if not is_valid_pin(account_number, old_pin):
        return {'status': 'error', 'message': 'Nieprawidłowy PIN'}
    if not is_valid_pin_format(new_pin):
        return {'status': 'error', 'message': 'Nieprawidłowy format PIN-u'}

    # Logika zmiany PIN-u
    # Zaktualizuj PIN konta
    update_account_pin(account_number, new_pin)

    return {'status': 'success', 'message': 'PIN został zmieniony'}

# Funkcja obsługująca żądanie logowania do konta
def login(account_number, pin):
    # Sprawdź poprawność danych wejściowych
    if not account_exists(account_number):
        return {'status': 'error', 'message': 'Konto nie istnieje'}
    if not is_valid_pin(account_number, pin):
        return {'status': 'error', 'message': 'Nieprawidłowy PIN'}

    # Logika logowania do konta
    # Utwórz sesję dla konta

    return {'status': 'success', 'message': 'Zalogowano'}

# Funkcja obsługująca żądanie utworzenia nowego konta
def create_account(account_number, pin):
    # Sprawdź poprawność danych wejściowych
    if account_exists(account_number):
        return {'status': 'error', 'message': 'Konto już istnieje'}
    if not is_valid_pin_format(pin):
        return {'status': 'error', 'message': 'Nieprawidłowy format PIN-u'}

    # Logika tworzenia nowego konta
    # Dodaj konto do pliku z informacjami o kontach
    add_account(account_number, pin)
    # Dodaj wpis do historii transakcji
    add_transaction_to_history(account_number, 'Utworzenie konta', 0)

    return {'status': 'success', 'message': 'Konto zostało utworzone'}

# Funkcja obsługująca żądanie przesyłu środków między kontami
def transfer_funds(from_account, to_account, amount):
    # Sprawdź poprawność danych wejściowych
    if not account_exists(from_account):
        return {'status': 'error', 'message': 'Konto źródłowe nie istnieje'}
    if not account_exists(to_account):
        return {'status': 'error', 'message': 'Konto docelowe nie istnieje'}
    if amount <= 0:
        return {'status': 'error', 'message': 'Nieprawidłowa kwota'}
    if not has_sufficient_balance(from_account, amount):
        return {'status': 'error', 'message': 'Niewystarczające saldo na koncie źródłowym'}

    # Logika przesyłu środków między kontami
    # Zaktualizuj saldo kont
    update_account_balance(from_account, -amount)
    update_account_balance(to_account, amount)
    # Dodaj wpis do historii transakcji
    add_transaction_to_history(from_account, f'Przelew (-{amount})', 0)
    add_transaction_to_history(to_account, f'Przelew (+{amount})', 0)

    return {'status': 'success', 'message': f'Przełano {amount} jednostek waluty z konta {from_account} na konto {to_account}'}

# Funkcja obsługująca żądanie zakończenia sesji
def end_session(account_number):
    # Logika zakończenia sesji
    # Usuń sesję dla konta

    return {'status': 'success', 'message': 'Sesja została zakończona'}

# Funkcja sprawdzająca, czy konto istnieje
def account_exists(account_number):
    # Sprawdź, czy konto istnieje na podstawie pliku z informacjami o kontach
    with open(BANK_ACCOUNTS_FILE, 'r') as f:
        accounts_data = json.load(f)
        accounts = accounts_data['accounts']
        for account in accounts:
            if account['account_number'] == account_number:
                return True
    return False

# Funkcja sprawdzająca, czy konto ma wystarczające saldo
def has_sufficient_balance(account_number, amount):
    # Sprawdź, czy konto ma wystarczające saldo na podstawie pliku z informacjami o kontach
    with open(BANK_ACCOUNTS_FILE, 'r') as f:
        accounts_data = json.load(f)
        accounts = accounts_data['accounts']
        for account in accounts:
            if account['account_number'] == account_number:
                return account['balance'] >= amount
    return False

# Funkcja zwracająca saldo konta
def get_account_balance(account_number):
    # Zwróć saldo konta na podstawie pliku z informacjami o kontach
    with open(BANK_ACCOUNTS_FILE, 'r') as f:
        accounts_data = json.load(f)
        accounts = accounts_data['accounts']
        for account in accounts:
            if account['account_number'] == account_number:
                return account['balance']
    return 0

# Funkcja aktualizująca saldo konta
def update_account_balance(account_number, amount):
    # Zaktualizuj saldo konta na podstawie pliku z informacjami o kontach
    with open(BANK_ACCOUNTS_FILE, 'r') as f:
        accounts_data = json.load(f)
        accounts = accounts_data['accounts']
        for account in accounts:
            if account['account_number'] == account_number:
                account['balance'] += amount
                break
    with open(BANK_ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts_data, f, indent=4)

# Funkcja dodająca konto do pliku z informacjami o kontach
def add_account(account_number, pin):
    # Dodaj konto do pliku z informacjami o kontach
    with open(BANK_ACCOUNTS_FILE, 'r') as f:
        accounts_data = json.load(f)
        accounts = accounts_data['accounts']
        accounts.append({
            'account_number': account_number,
            'pin': pin,
            'balance': 0
        })
    with open(BANK_ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts_data, f, indent=4)

# Funkcja sprawdzająca, czy PIN jest poprawny dla danego konta
def is_valid_pin(account_number, pin):
    # Sprawdź, czy PIN jest poprawny na podstawie pliku z informacjami o kontach
    with open(BANK_ACCOUNTS_FILE, 'r') as f:
        accounts_data = json.load(f)
        accounts = accounts_data['accounts']
        for account in accounts:
            if account['account_number'] == account_number:
                return account['pin'] == pin
    return False

# Funkcja sprawdzająca poprawność formatu PIN-u
def is_valid_pin_format(pin):
    # Sprawdź, czy PIN ma poprawny format (4 cyfry)
    return len(pin) == 4 and pin.isdigit()

# Funkcja dodająca wpis do historii transakcji
def add_transaction_to_history(account_number, description, amount):
    # Dodaj wpis do historii transakcji w pliku
    with open(TRANSACTION_HISTORY_FILE, 'r') as f:
        history_data = json.load(f)
        history = history_data['history']
        history.append({
            'account_number': account_number,
            'description': description,
            'amount': amount
        })
    with open(TRANSACTION_HISTORY_FILE, 'w') as f:
        json.dump(history_data, f, indent=4)

# Główna pętla serwera
def start_server():
    # Inicjalizacja serwera
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(1)

    print('Serwer bankomatu uruchomiony.')

    while True:
        # Oczekiwanie na połączenie
        client_socket, address = server_socket.accept()
        print(f'Połączono z klientem {address}')

        while True:
            # Oczekiwanie na dane od klienta
            data = client_socket.recv(1024)
            if not data:
                break

            # Przetwarzanie żądania klienta
            request = json.loads(data.decode('utf-8'))
            response = process_request(request)

            # Wysłanie odpowiedzi do klienta
            client_socket.send(json.dumps(response).encode('utf-8'))

        # Zamknięcie połączenia
        client_socket.close()

    # Zamknięcie serwera
    server_socket.close()

# Funkcja przetwarzająca żądanie klienta
def process_request(request):
    command = request['command']
    if command == 'withdraw':
        return withdraw_amount(request['account_number'], request['amount'])
    elif command == 'deposit':
        return deposit_amount(request['account_number'], request['amount'])
    elif command == 'balance':
        return check_balance(request['account_number'])
    elif command == 'change_pin':
        return change_pin(request['account_number'], request['old_pin'], request['new_pin'])
    elif command == 'login':
        return login(request['account_number'], request['pin'])
    elif command == 'create_account':
        return create_account(request['account_number'], request['pin'])
    elif command == 'transfer':
        return transfer_funds(request['from_account'], request['to_account'], request['amount'])
    elif command == 'end_session':
        return end_session(request['account_number'])
    else:
        return {'status': 'error', 'message': 'Nieprawidłowe żądanie'}

# Uruchomienie serwera bankomatu
start_server()
