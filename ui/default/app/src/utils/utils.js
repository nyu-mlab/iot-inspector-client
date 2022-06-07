export const dataUseage = (bytes) => {
  if (bytes >= 1000000) {
    return `${parseFloat(bytes / 1000000).toFixed(2)} MB`
  }
  if (bytes >= 1000) {
    return `${parseFloat(bytes / 1000).toFixed(2)} KB`
  }
  return `${parseFloat(bytes).toFixed(2)} BYTES`
}