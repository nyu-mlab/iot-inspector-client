import { addDays, addMonths, addHours, differenceInDays, differenceInMonths, differenceInHours } from 'date-fns';

export const dataUseage = (bytes) => {
  if (bytes >= 1000000) {
    return `${parseFloat(bytes / 1000000).toFixed(2)} MB`
  }
  if (bytes >= 1000) {
    return `${parseFloat(bytes / 1000).toFixed(2)} KB`
  }
  return `${parseFloat(bytes).toFixed(2)} BYTES`
}

export const datesBetween = (startDate, endDate, interval = "hour") => {
  if (interval === "day") {
    const days = differenceInDays(endDate, startDate);
    return [ ...Array(days + 1).keys() ].map((i) => addDays(startDate, i));
  }

  if (interval === "hour") {
    const hours = differenceInHours(endDate, startDate);
    return [ ...Array(hours + 1).keys() ].map((i) => addHours(startDate, i));
  }

  if (interval === "month") {
    const months = differenceInMonths(endDate, startDate);
    return [ ...Array(months + 1).keys() ].map((i) => addMonths(startDate, i));
  }
}