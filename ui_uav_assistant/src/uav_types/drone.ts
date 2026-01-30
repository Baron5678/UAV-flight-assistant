export interface Drone {
    batteryWh: number;
    whPerKm: number;
    reserveRatio?: number;
    speed: number
}