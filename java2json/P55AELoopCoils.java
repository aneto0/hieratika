import java.util.Arrays;
import java.util.Vector;

class P55AELoopCoils extends PMCVariable {

    public P55AELoopCoils() {
        super("AE", "55 AE loop coils", new Vector(), "", new int[]{1}, true, false, null);
    }

    PMCLoopCoil M0001 = new PMCLoopCoil("M0001", "55.AE.00-MCH-0001", false, 3.567,-3.49,3.567,-3.49,-180,180);
    PMCLoopCoil M0002 = new PMCLoopCoil("M0002", "55.AE.00-MCH-0002", false, 3.567,1.435,3.567,1.435,-180,180);
    PMCLoopCoil M0003 = new PMCLoopCoil("M0003", "55.AE.00-MCH-0003", false, 8.74743,1.82,8.74742,1.82,-180,180);
    PMCLoopCoil M0004 = new PMCLoopCoil("M0004", "55.AE.00-MCH-0004", false, 8.7659,-0.642,8.76591,-0.642,-180,180);
    PMCLoopCoil M1001 = new PMCLoopCoil("M1001", "55.AE.00-MCL-1001", false, 3.567,-2.61,3.56701,-2.61,14.94,43.46);
    PMCLoopCoil M1002 = new PMCLoopCoil("M1002", "55.AE.00-MCL-1002", false, 5.84746,5,5.84745,5,13.99,46.99);
    PMCLoopCoil M1003 = new PMCLoopCoil("M1003", "55.AE.00-MCL-1003", false, 8.35493,2.69,8.35492,2.69,12.79,47.89);
    PMCLoopCoil M1004 = new PMCLoopCoil("M1004", "55.AE.00-MCL-1004", false, 7.8711,-2.6,7.87111,-2.6,12.24,47.04);
    PMCLoopCoil M2001 = new PMCLoopCoil("M2001", "55.AE.00-MCL-2001", false, 3.567,-2.61,3.567,-2.61,54.94,83.46);
    PMCLoopCoil M2002 = new PMCLoopCoil("M2002", "55.AE.00-MCL-2002", false, 5.84746,5,5.84745,5,53.99,86.99);
    PMCLoopCoil M2003 = new PMCLoopCoil("M2003", "55.AE.00-MCL-2003", false, 8.35493,2.69,8.35492,2.69,52.79,87.89);
    PMCLoopCoil M2004 = new PMCLoopCoil("M2004", "55.AE.00-MCL-2004", false, 7.87109,-2.6,7.8711,-2.6,52.24,87.04);
    PMCLoopCoil M3001 = new PMCLoopCoil("M3001", "55.AE.00-MCL-3001", false, 3.56699,-2.61,3.567,-2.61,94.94,123.46);
    PMCLoopCoil M3002 = new PMCLoopCoil("M3002", "55.AE.00-MCL-3002", false, 5.84746,5,5.84745,5,93.99,126.99);
    PMCLoopCoil M3003 = new PMCLoopCoil("M3003", "55.AE.00-MCL-3003", false, 8.35493,2.69,8.35492,2.69,92.79,127.89);
    PMCLoopCoil M3004 = new PMCLoopCoil("M3004", "55.AE.00-MCL-3004", false, 7.8711,-2.6,7.8711,-2.6,92.24,127.04);
    PMCLoopCoil M4001 = new PMCLoopCoil("M4001", "55.AE.00-MCL-4001", false, 3.567,-2.61,3.567,-2.61,134.94,163.46);
    PMCLoopCoil M4002 = new PMCLoopCoil("M4002", "55.AE.00-MCL-4002", false, 5.84746,5,5.84745,5,133.99,166.99);
    PMCLoopCoil M4003 = new PMCLoopCoil("M4003", "55.AE.00-MCL-4003", false, 8.35493,2.69,8.35492,2.69,132.79,167.89);
    PMCLoopCoil M4004 = new PMCLoopCoil("M4004", "55.AE.00-MCL-4004", false, 7.87109,-2.6,7.87111,-2.6,132.24,167.04);
    PMCLoopCoil M5001 = new PMCLoopCoil("M5001", "55.AE.00-MCL-5001", false, 3.567,-2.61,3.567,-2.61,-185.06,-156.54);
    PMCLoopCoil M5002 = new PMCLoopCoil("M5002", "55.AE.00-MCL-5002", false, 5.84746,5,5.84745,5,173.99,206.99);
    PMCLoopCoil M5003 = new PMCLoopCoil("M5003", "55.AE.00-MCL-5003", false, 8.35493,2.69,8.35492,2.69,172.79,207.89);
    PMCLoopCoil M5004 = new PMCLoopCoil("M5004", "55.AE.00-MCL-5004", false, 7.87109,-2.6,7.8711,-2.6,-187.76,-152.96);
    PMCLoopCoil M6001 = new PMCLoopCoil("M6001", "55.AE.00-MCL-6001", false, 3.567,-2.61,3.567,-2.61,-145.06,-116.54);
    PMCLoopCoil M6002 = new PMCLoopCoil("M6002", "55.AE.00-MCL-6002", false, 5.84746,5,5.84745,5,-146.01,-113.01);
    PMCLoopCoil M6003 = new PMCLoopCoil("M6003", "55.AE.00-MCL-6003", false, 8.35493,2.69,8.35492,2.69,-147.21,-112.11);
    PMCLoopCoil M6004 = new PMCLoopCoil("M6004", "55.AE.00-MCL-6004", false, 7.87109,-2.6,7.87111,-2.6,-147.76,-112.96);
    PMCLoopCoil M7001 = new PMCLoopCoil("M7001", "55.AE.00-MCL-7001", false, 3.567,-2.61,3.567,-2.61,-105.06,-76.54);
    PMCLoopCoil M7002 = new PMCLoopCoil("M7002", "55.AE.00-MCL-7002", false, 5.84746,5,5.84745,5,-106.01,-73.01);
    PMCLoopCoil M7003 = new PMCLoopCoil("M7003", "55.AE.00-MCL-7003", false, 8.35493,2.69,8.35492,2.69,-107.21,-72.11);
    PMCLoopCoil M7004 = new PMCLoopCoil("M7004", "55.AE.00-MCL-7004", false, 7.87109,-2.6,7.8711,-2.6,-107.76,-72.96);
    PMCLoopCoil M8001 = new PMCLoopCoil("M8001", "55.AE.00-MCL-8001", false, 3.567,-2.61,3.567,-2.61,-65.06,-36.54);
    PMCLoopCoil M8002 = new PMCLoopCoil("M8002", "55.AE.00-MCL-8002", false, 5.84746,5,5.84745,5,-66.01,-33.01);
    PMCLoopCoil M8003 = new PMCLoopCoil("M8003", "55.AE.00-MCL-8003", false, 8.35493,2.69,8.35492,2.69,-67.21,-32.11);
    PMCLoopCoil M8004 = new PMCLoopCoil("M8004", "55.AE.00-MCL-8004", false, 7.87109,-2.6,7.8711,-2.6,-67.76,-32.96);
    PMCLoopCoil M9001 = new PMCLoopCoil("M9001", "55.AE.00-MCL-9001", false, 3.567,-2.61,3.567,-2.61,-25.06,3.46);
    PMCLoopCoil M9002 = new PMCLoopCoil("M9002", "55.AE.00-MCL-9002", false, 5.84746,5,5.84745,5,-26.01,6.99);
    PMCLoopCoil M9003 = new PMCLoopCoil("M9003", "55.AE.00-MCL-9003", false, 8.35493,2.69,8.35492,2.69,-27.21,7.89);
    PMCLoopCoil M9004 = new PMCLoopCoil("M9004", "55.AE.00-MCL-9004", false, 7.8711,-2.6,7.8711,-2.6,-27.76,7.04);


}


