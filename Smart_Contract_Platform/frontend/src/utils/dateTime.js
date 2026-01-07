// 格式化日期时间（将UTC时间转换为中国时区 UTC+8）
export function formatDateTime(dateTimeStr) {
  if (!dateTimeStr) return ''
  try {
    // 如果时间字符串没有时区标识（没有Z），添加Z表示UTC时间
    let utcStr = dateTimeStr
    if (typeof utcStr === 'string' && !utcStr.endsWith('Z') && !utcStr.includes('+') && !utcStr.includes('-', 10)) {
      // 如果字符串格式是 "2026-01-06T03:39:08.123456"，添加Z
      // 检查是否包含时间部分（T后面有数字）
      if (utcStr.includes('T') && /T\d/.test(utcStr)) {
        utcStr = utcStr + 'Z'
      }
    }
    const date = new Date(utcStr)
    // 使用 toLocaleString 并指定时区为中国时区
    return date.toLocaleString('zh-CN', {
      timeZone: 'Asia/Shanghai',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  } catch (e) {
    return dateTimeStr
  }
}

