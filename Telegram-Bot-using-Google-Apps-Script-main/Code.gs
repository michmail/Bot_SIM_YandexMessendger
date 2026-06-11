const spreadsheetId = '1GL23wXYZTMqGsWcRAn6pmehBWGTpwTbPdnzT2d7Y8uk'; // ID Spreadsheet
const anggotaSheetName = 'Data Anggota'; // Sheet untuk menyimpan data anggota
const logSheetName = 'Log'; // Sheet untuk log
const dataChatSheetName = 'Data Chat'; // Sheet untuk menyimpan data chat
const botToken = '7676986534:AAED64eZJWrVE6anttVkRse1th9UjM-YpZA';
const telegramApiUrl = `https://api.telegram.org/bot${botToken}`;

// Fungsi untuk mencatat log
function log(logMessage = '') {
  const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  const sheet = spreadsheet.getSheetByName(logSheetName);
  sheet.appendRow([formatTimestamp(new Date()), logMessage]);
}

// Fungsi untuk format timestamp
function formatTimestamp(date) {
  return Utilities.formatDate(date, Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm:ss');
}

// Fungsi untuk mendapatkan data anggota berdasarkan username
function getAnggotaData(username) {
  const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  const sheet = spreadsheet.getSheetByName(anggotaSheetName);
  const data = sheet.getDataRange().getValues();

  for (let i = 1; i < data.length; i++) {
    if (data[i][2] === username) {
      return { nip: data[i][3], noHp: data[i][4], status: data[i][5] }; // Mendapatkan status
    }
  }
  return null; // Jika username tidak ditemukan
}

// Fungsi untuk mengirim pesan Telegram
function sendTelegramMessage(chatId, replyToMessageId, textMessage, keyboard = null) {
  const url = `${telegramApiUrl}/sendMessage`;
  const data = {
    chat_id: chatId,
    text: textMessage,
    parse_mode: 'HTML',
    reply_to_message_id: replyToMessageId,
    disable_web_page_preview: true,
  };

  if (keyboard) {
    data.reply_markup = JSON.stringify(keyboard);
  }

  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(data),
  };

  UrlFetchApp.fetch(url, options);
}

// Fungsi untuk menyimpan atau memperbarui data anggota
function saveOrUpdateAnggota(username, firstName, nip, noHp, status = 'Tersimpan') {
  const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  const sheet = spreadsheet.getSheetByName(anggotaSheetName);
  const data = sheet.getDataRange().getValues();

  let updated = false;
  for (let i = 1; i < data.length; i++) {
    if (data[i][2] === username) {
      // Jika data sudah ada dan statusnya 'Tersimpan', beri tahu pengguna untuk menghapus data terlebih dahulu
      if (data[i][5] === 'Tersimpan') {
        return 'Data Anda sudah tersimpan. Silakan hapus data terlebih dahulu jika ingin memperbarui.';
      }

      // Pastikan NIP dan No HP disimpan sebagai teks
      sheet.getRange(i + 1, 4).setValue(`'${nip}`); // Update NIP sebagai teks
      sheet.getRange(i + 1, 5).setValue(`'${noHp}`); // Update No HP sebagai teks
      sheet.getRange(i + 1, 6).setValue(status); // Update status
      updated = true;
      log(`Data anggota diperbarui untuk ${username}`);
      break;
    }
  }

  if (!updated) {
    sheet.appendRow([formatTimestamp(new Date()), firstName, username, `'${nip}`, `'${noHp}`, status]);
    log(`Data anggota disimpan untuk ${username}`);
  }

  return 'Data berhasil disimpan.';
}


// Fungsi untuk menghapus data anggota
function deleteAnggota(username) {
  const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  const sheet = spreadsheet.getSheetByName(anggotaSheetName);
  const data = sheet.getDataRange().getValues();

  for (let i = 1; i < data.length; i++) {
    if (data[i][2] === username) {
      sheet.getRange(i + 1, 6).setValue('Terhapus'); // Set status "Terhapus"
      log(`Data anggota dihapus untuk ${username}`);
      return true;
    }
  }
  return false; // Data tidak ditemukan
}

// Fungsi untuk menyimpan data chat ke Spreadsheet
function saveToSheet(sheetName, rowData) {
  const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  const sheet = spreadsheet.getSheetByName(sheetName);
  
  // Menyimpan NIP dan No HP sebagai teks dengan menambahkan tanda petik agar angka 0 di awal tetap terbaca
  rowData[3] = `'${rowData[3]}`; // Pastikan NIP disimpan sebagai teks
  rowData[4] = `'${rowData[4]}`; // Pastikan No HP disimpan sebagai teks
  
  sheet.appendRow(rowData);
}


// Fungsi untuk menangani update dari Telegram
function doPost(e) {
  const contents = JSON.parse(e.postData.contents);
  const chatId = contents.message.chat.id;
  const messageId = contents.message.message_id;
  const username = contents.message.from.username || '';
  const firstName = contents.message.from.first_name || '';
  const userProperties = PropertiesService.getUserProperties();
  const awaitingInput = userProperties.getProperty(`awaitingInput_${chatId}`);
  const receivedTextMessage = contents.message.text?.trim() || '';

  let messageReply = '';

  // Jika user mengetikkan /start
  if (receivedTextMessage === '/start') {
    messageReply = `Selamat datang! Silakan gunakan /menu untuk mulai.`;
    sendTelegramMessage(chatId, messageId, messageReply);
    return;
  }

  // Jika user sedang dalam mode memasukkan data
  if (awaitingInput) {
    // Regex untuk mencocokkan NIP dan No HP dalam format yang terpisah
    const inputRegex = /^NIP:\s*(\d+)\s*No HP:\s*(\d+)/i;
    const match = receivedTextMessage.match(inputRegex);

    if (match) {
      const nip = match[1];
      const noHp = match[2];
      const saveMessage = saveOrUpdateAnggota(username, firstName, nip, noHp, 'Tersimpan');
      userProperties.deleteProperty(`awaitingInput_${chatId}`);
      messageReply = saveMessage;
    } else {
      messageReply = 'Format salah. Silakan gunakan format berikut:\nNIP: [isi NIP]\nNo HP: [isi No HP]';
    }
    sendTelegramMessage(chatId, messageId, messageReply);
    return;
  }

  // Jika user mengetikkan /menu
  if (receivedTextMessage === '/menu') {
    const keyboard = {
      keyboard: [
        [{ text: 'Masukkan Data' }],
        [{ text: 'Lihat Data Saya' }],
        [{ text: 'Hapus Data' }],
      ],
      resize_keyboard: true,
      one_time_keyboard: true,
    };
    messageReply = 'Pilih menu di bawah ini:';
    sendTelegramMessage(chatId, messageId, messageReply, keyboard);
    return;
  }

  // Jika user memilih "Masukkan Data"
  if (receivedTextMessage === 'Masukkan Data') {
    const anggotaData = getAnggotaData(username);
    if (anggotaData && anggotaData.status === 'Tersimpan') {
      messageReply = 'Data Anda sudah tersimpan. Silakan hapus data terlebih dahulu jika ingin memperbarui.';
    } else {
      userProperties.setProperty(`awaitingInput_${chatId}`, 'true');
      messageReply = 'Silakan masukkan data Anda dengan format:\nNIP: [isi NIP]\nNo HP: [isi No HP]';
    }
    sendTelegramMessage(chatId, messageId, messageReply);
    return;
  }

  // Jika user memilih "Lihat Data Saya"
  if (receivedTextMessage === 'Lihat Data Saya') {
    const anggotaData = getAnggotaData(username);
    if (anggotaData) {
      messageReply = `Data Anda:\n- NIP: ${anggotaData.nip}\n- No HP: ${anggotaData.noHp}\n- Status: ${anggotaData.status}`;
    } else {
      messageReply = 'Data Anda belum terdaftar.';
    }
    sendTelegramMessage(chatId, messageId, messageReply);
    return;
  }

  // Jika user memilih "Hapus Data"
  if (receivedTextMessage === 'Hapus Data') {
    const deleted = deleteAnggota(username);
    messageReply = deleted ? 'Data Anda berhasil dihapus.' : 'Data Anda tidak ditemukan.';
    sendTelegramMessage(chatId, messageId, messageReply);
    return;
  }

  // Menyimpan pesan di grup ke Data Chat dengan informasi NIP dan No HP
  const anggotaData = getAnggotaData(username);
  let nip = 'Belum terdaftar';
  let noHp = 'Belum terdaftar';

  if (anggotaData) {
    if (anggotaData.status === 'Terhapus') {
      nip = 'Belum terdaftar';
      noHp = 'Belum terdaftar';
    } else {
      nip = anggotaData.nip;
      noHp = anggotaData.noHp;
    }
  }

  // Simpan hanya jika bukan interaksi dengan bot
  if (!receivedTextMessage.startsWith('/')) {
    saveToSheet(dataChatSheetName, [
      formatTimestamp(new Date()),
      firstName,
      username,
      nip,
      noHp,
      receivedTextMessage,
    ]);
  }
}
