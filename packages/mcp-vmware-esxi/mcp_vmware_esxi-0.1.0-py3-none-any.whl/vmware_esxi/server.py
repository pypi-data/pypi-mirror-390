#!/usr/bin/env python3
"""
Serveur MCP pour la gestion VMware vSphere/ESXi
"""

import os
import json
import logging
import ssl
import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from pyVim import connect
from pyVmomi import vim, vmodl

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    vcenter_host: str
    vcenter_user: str
    vcenter_password: str
    datacenter: Optional[str] = None
    cluster: Optional[str] = None
    datastore: Optional[str] = None
    network: Optional[str] = None
    insecure: bool = False

class VMwareManager:
    """Classe de gestion VMware vSphere/ESXi"""
    
    def __init__(self, config: Config):
        self.config = config
        self.si = None
        self.content = None
        self.datacenter_obj = None
        self.resource_pool = None
        self.datastore_obj = None
        self.network_obj = None
        self._connect_vcenter()

    def _connect_vcenter(self):
        """Connexion à vCenter/ESXi"""
        try:
            if self.config.insecure:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                self.si = connect.SmartConnect(
                    host=self.config.vcenter_host,
                    user=self.config.vcenter_user,
                    pwd=self.config.vcenter_password,
                    sslContext=context
                )
            else:
                self.si = connect.SmartConnect(
                    host=self.config.vcenter_host,
                    user=self.config.vcenter_user,
                    pwd=self.config.vcenter_password
                )
        except Exception as e:
            logger.error(f"Échec de connexion à vCenter/ESXi: {e}")
            raise

        self.content = self.si.RetrieveContent()
        logger.info("Connexion réussie à VMware vCenter/ESXi")

        # Récupération du datacenter
        if self.config.datacenter:
            self.datacenter_obj = next(
                (dc for dc in self.content.rootFolder.childEntity
                 if isinstance(dc, vim.Datacenter) and dc.name == self.config.datacenter),
                None
            )
            if not self.datacenter_obj:
                raise Exception(f"Datacenter {self.config.datacenter} non trouvé")
        else:
            self.datacenter_obj = next(
                (dc for dc in self.content.rootFolder.childEntity
                 if isinstance(dc, vim.Datacenter)),
                None
            )
        
        if not self.datacenter_obj:
            raise Exception("Aucun datacenter trouvé")

        # Récupération du resource pool
        compute_resource = None
        if self.config.cluster:
            for folder in self.datacenter_obj.hostFolder.childEntity:
                if isinstance(folder, vim.ClusterComputeResource) and folder.name == self.config.cluster:
                    compute_resource = folder
                    break
            if not compute_resource:
                raise Exception(f"Cluster {self.config.cluster} non trouvé")
        else:
            compute_resource = next(
                (cr for cr in self.datacenter_obj.hostFolder.childEntity
                 if isinstance(cr, vim.ComputeResource)),
                None
            )
        
        if not compute_resource:
            raise Exception("Aucune ressource de calcul trouvée")
        
        self.resource_pool = compute_resource.resourcePool
        logger.info(f"Utilisation du resource pool: {self.resource_pool.name}")

        # Récupération du datastore
        if self.config.datastore:
            self.datastore_obj = next(
                (ds for ds in self.datacenter_obj.datastoreFolder.childEntity
                 if isinstance(ds, vim.Datastore) and ds.name == self.config.datastore),
                None
            )
            if not self.datastore_obj:
                raise Exception(f"Datastore {self.config.datastore} non trouvé")
        else:
            datastores = [
                ds for ds in self.datacenter_obj.datastoreFolder.childEntity
                if isinstance(ds, vim.Datastore)
            ]
            if not datastores:
                raise Exception("Aucun datastore disponible")
            self.datastore_obj = max(datastores, key=lambda ds: ds.summary.freeSpace)
        
        logger.info(f"Utilisation du datastore: {self.datastore_obj.name}")

        # Récupération du réseau
        if self.config.network:
            self.network_obj = next(
                (net for net in self.datacenter_obj.networkFolder.childEntity
                 if hasattr(net, 'name') and net.name == self.config.network),
                None
            )
            if not self.network_obj:
                raise Exception(f"Réseau {self.config.network} non trouvé")
        else:
            networks = [
                net for net in self.datacenter_obj.networkFolder.childEntity
                if isinstance(net, (vim.Network, vim.DistributedVirtualPortgroup))
            ]
            if networks:
                self.network_obj = networks[0]
        
        if self.network_obj:
            logger.info(f"Utilisation du réseau: {self.network_obj.name}")

    def find_vm(self, vm_name: str) -> Optional[vim.VirtualMachine]:
        """Recherche une VM par son nom"""
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        try:
            for vm in container.view:
                if vm.name == vm_name:
                    return vm
            return None
        finally:
            container.Destroy()

    def list_vms(self) -> List[str]:
        """Liste toutes les VMs"""
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        try:
            return [vm.name for vm in container.view]
        finally:
            container.Destroy()

    def get_vm_info(self, vm: vim.VirtualMachine) -> Dict[str, Any]:
        """Récupère les informations d'une VM"""
        summary = vm.summary
        config = vm.config
        runtime = vm.runtime
        
        info = {
            "name": vm.name,
            "power_state": runtime.powerState,
            "guest_os": config.guestFullName if config else "Unknown",
            "cpu": config.hardware.numCPU if config else 0,
            "memory_mb": config.hardware.memoryMB if config else 0,
            "num_disks": len(config.hardware.device) if config else 0,
            "ip_address": summary.guest.ipAddress if summary.guest else None,
            "host": runtime.host.name if runtime.host else None,
            "uptime_seconds": summary.quickStats.uptimeSeconds if summary.quickStats else 0,
        }
        
        # Informations sur les disques
        if config:
            disks = []
            for device in config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualDisk):
                    disks.append({
                        "label": device.deviceInfo.label,
                        "capacity_gb": device.capacityInKB / (1024 * 1024),
                        "datastore": device.backing.datastore.name if hasattr(device.backing, 'datastore') else None
                    })
            info["disks"] = disks
        
        # Informations réseau
        if config:
            networks = []
            for device in config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualEthernetCard):
                    networks.append({
                        "label": device.deviceInfo.label,
                        "mac_address": device.macAddress,
                        "network": device.backing.network.name if hasattr(device.backing, 'network') else None
                    })
            info["networks"] = networks
        
        return info

    def create_vm(
        self,
        name: str,
        cpu: int,
        memory_mb: int,
        disk_gb: int,
        guest_id: str = "ubuntu64Guest"
    ) -> str:
        """Crée une nouvelle VM"""
        
        # Configuration de la VM
        vm_config = vim.vm.ConfigSpec(
            name=name,
            memoryMB=memory_mb,
            numCPUs=cpu,
            guestId=guest_id,
            files=vim.vm.FileInfo(
                vmPathName=f"[{self.datastore_obj.name}]"
            )
        )
        
        # Configuration du disque
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        disk_spec.fileOperation = vim.vm.device.VirtualDeviceSpec.FileOperation.create
        
        disk = vim.vm.device.VirtualDisk()
        disk.capacityInKB = disk_gb * 1024 * 1024
        disk.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        disk.backing.diskMode = 'persistent'
        disk.backing.datastore = self.datastore_obj
        
        disk.controllerKey = 1000
        disk.unitNumber = 0
        disk_spec.device = disk
        
        # Contrôleur SCSI
        scsi_spec = vim.vm.device.VirtualDeviceSpec()
        scsi_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        scsi_controller = vim.vm.device.ParaVirtualSCSIController()
        scsi_controller.key = 1000
        scsi_controller.busNumber = 0
        scsi_controller.sharedBus = vim.vm.device.VirtualSCSIController.Sharing.noSharing
        scsi_spec.device = scsi_controller
        
        # Configuration réseau
        network_spec = vim.vm.device.VirtualDeviceSpec()
        network_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        
        nic = vim.vm.device.VirtualVmxnet3()
        nic.key = 4000
        
        if isinstance(self.network_obj, vim.DistributedVirtualPortgroup):
            nic.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
            nic.backing.port = vim.dvs.PortConnection()
            nic.backing.port.portgroupKey = self.network_obj.key
            nic.backing.port.switchUuid = self.network_obj.config.distributedVirtualSwitch.uuid
        else:
            nic.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
            nic.backing.network = self.network_obj
            nic.backing.deviceName = self.network_obj.name
        
        nic.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic.connectable.startConnected = True
        nic.connectable.allowGuestControl = True
        nic.connectable.connected = True
        network_spec.device = nic
        
        vm_config.deviceChange = [scsi_spec, disk_spec, network_spec]
        
        # Création de la VM
        task = self.datacenter_obj.vmFolder.CreateVM_Task(
            config=vm_config,
            pool=self.resource_pool
        )
        
        # Attendre la fin de la tâche
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            pass
        
        if task.info.state == vim.TaskInfo.State.error:
            raise Exception(f"Erreur lors de la création de la VM: {task.info.error}")
        
        return f"VM '{name}' créée avec succès"

    def delete_vm(self, vm: vim.VirtualMachine) -> str:
        """Supprime une VM"""
        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
            task = vm.PowerOff()
            while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                pass
        
        task = vm.Destroy_Task()
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            pass
        
        if task.info.state == vim.TaskInfo.State.error:
            raise Exception(f"Erreur lors de la suppression: {task.info.error}")
        
        return f"VM '{vm.name}' supprimée avec succès"

    def disconnect(self):
        """Déconnexion de vCenter"""
        if self.si:
            connect.Disconnect(self.si)
            logger.info("Déconnexion de vCenter")


# Création du serveur MCP
app = Server("vmware-server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Liste des outils VMware disponibles"""
    return [
        types.Tool(
            name="vmware_list_vms",
            description="Liste toutes les machines virtuelles VMware",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="vmware_get_vm_info",
            description="Obtenir les informations détaillées d'une machine virtuelle",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_name": {
                        "type": "string",
                        "description": "Nom de la machine virtuelle"
                    }
                },
                "required": ["vm_name"]
            }
        ),
        types.Tool(
            name="vmware_power_on_vm",
            description="Démarrer une machine virtuelle",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_name": {
                        "type": "string",
                        "description": "Nom de la machine virtuelle à démarrer"
                    }
                },
                "required": ["vm_name"]
            }
        ),
        types.Tool(
            name="vmware_power_off_vm",
            description="Arrêter une machine virtuelle",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_name": {
                        "type": "string",
                        "description": "Nom de la machine virtuelle à arrêter"
                    }
                },
                "required": ["vm_name"]
            }
        ),
        types.Tool(
            name="vmware_reboot_vm",
            description="Redémarrer une machine virtuelle",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_name": {
                        "type": "string",
                        "description": "Nom de la machine virtuelle à redémarrer"
                    }
                },
                "required": ["vm_name"]
            }
        ),
        types.Tool(
            name="vmware_create_vm",
            description="Créer une nouvelle machine virtuelle",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Nom de la nouvelle VM"
                    },
                    "cpu": {
                        "type": "integer",
                        "description": "Nombre de CPUs"
                    },
                    "memory_mb": {
                        "type": "integer",
                        "description": "Mémoire en MB"
                    },
                    "disk_gb": {
                        "type": "integer",
                        "description": "Taille du disque en GB"
                    },
                    "guest_id": {
                        "type": "string",
                        "description": "ID du système d'exploitation invité (ex: ubuntu64Guest)",
                        "default": "ubuntu64Guest"
                    }
                },
                "required": ["name", "cpu", "memory_mb", "disk_gb"]
            }
        ),
        types.Tool(
            name="vmware_delete_vm",
            description="Supprimer une machine virtuelle",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_name": {
                        "type": "string",
                        "description": "Nom de la machine virtuelle à supprimer"
                    }
                },
                "required": ["vm_name"]
            }
        ),
        types.Tool(
            name="vmware_create_snapshot",
            description="Créer un snapshot d'une machine virtuelle",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_name": {
                        "type": "string",
                        "description": "Nom de la machine virtuelle"
                    },
                    "snapshot_name": {
                        "type": "string",
                        "description": "Nom du snapshot"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description du snapshot",
                        "default": ""
                    },
                    "memory": {
                        "type": "boolean",
                        "description": "Inclure la mémoire dans le snapshot",
                        "default": False
                    }
                },
                "required": ["vm_name", "snapshot_name"]
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Exécuter un outil VMware"""
    
    # Charger la configuration depuis les variables d'environnement
    config = Config(
        vcenter_host=os.getenv("VCENTER_HOST", ""),
        vcenter_user=os.getenv("VCENTER_USER", ""),
        vcenter_password=os.getenv("VCENTER_PASSWORD", ""),
        datacenter=os.getenv("VCENTER_DATACENTER"),
        cluster=os.getenv("VCENTER_CLUSTER"),
        datastore=os.getenv("VCENTER_DATASTORE"),
        network=os.getenv("VCENTER_NETWORK"),
        insecure=os.getenv("VCENTER_INSECURE", "false").lower() == "true"
    )
    
    if not config.vcenter_host or not config.vcenter_user or not config.vcenter_password:
        return [types.TextContent(
            type="text",
            text="Erreur: Variables d'environnement VCENTER_HOST, VCENTER_USER et VCENTER_PASSWORD requises"
        )]
    
    manager = None
    try:
        manager = VMwareManager(config)
        
        if name == "vmware_list_vms":
            vms = manager.list_vms()
            result = {
                "count": len(vms),
                "vms": vms
            }
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
            
        elif name == "vmware_get_vm_info":
            vm = manager.find_vm(arguments["vm_name"])
            if not vm:
                return [types.TextContent(
                    type="text",
                    text=f"VM '{arguments['vm_name']}' non trouvée"
                )]
            info = manager.get_vm_info(vm)
            return [types.TextContent(
                type="text",
                text=json.dumps(info, indent=2, ensure_ascii=False)
            )]
            
        elif name == "vmware_power_on_vm":
            vm = manager.find_vm(arguments["vm_name"])
            if not vm:
                return [types.TextContent(
                    type="text",
                    text=f"VM '{arguments['vm_name']}' non trouvée"
                )]
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                return [types.TextContent(
                    type="text",
                    text=f"VM '{arguments['vm_name']}' est déjà démarrée"
                )]
            task = vm.PowerOn()
            return [types.TextContent(
                type="text",
                text=f"VM '{arguments['vm_name']}' en cours de démarrage"
            )]
            
        elif name == "vmware_power_off_vm":
            vm = manager.find_vm(arguments["vm_name"])
            if not vm:
                return [types.TextContent(
                    type="text",
                    text=f"VM '{arguments['vm_name']}' non trouvée"
                )]
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                return [types.TextContent(
                    type="text",
                    text=f"VM '{arguments['vm_name']}' est déjà arrêtée"
                )]
            task = vm.PowerOff()
            return [types.TextContent(
                type="text",
                text=f"VM '{arguments['vm_name']}' en cours d'arrêt"
            )]
            
        elif name == "vmware_reboot_vm":
            vm = manager.find_vm(arguments["vm_name"])
            if not vm:
                return [types.TextContent(
                    type="text",
                    text=f"VM '{arguments['vm_name']}' non trouvée"
                )]
            if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOn:
                return [types.TextContent(
                    type="text",
                    text=f"VM '{arguments['vm_name']}' n'est pas démarrée"
                )]
            vm.RebootGuest()
            return [types.TextContent(
                type="text",
                text=f"VM '{arguments['vm_name']}' en cours de redémarrage"
            )]
            
        elif name == "vmware_create_vm":
            result = manager.create_vm(
                name=arguments["name"],
                cpu=arguments["cpu"],
                memory_mb=arguments["memory_mb"],
                disk_gb=arguments["disk_gb"],
                guest_id=arguments.get("guest_id", "ubuntu64Guest")
            )
            return [types.TextContent(
                type="text",
                text=result
            )]
            
        elif name == "vmware_delete_vm":
            vm = manager.find_vm(arguments["vm_name"])
            if not vm:
                return [types.TextContent(
                    type="text",
                    text=f"VM '{arguments['vm_name']}' non trouvée"
                )]
            result = manager.delete_vm(vm)
            return [types.TextContent(
                type="text",
                text=result
            )]
            
        elif name == "vmware_create_snapshot":
            vm = manager.find_vm(arguments["vm_name"])
            if not vm:
                return [types.TextContent(
                    type="text",
                    text=f"VM '{arguments['vm_name']}' non trouvée"
                )]
            task = vm.CreateSnapshot_Task(
                name=arguments["snapshot_name"],
                description=arguments.get("description", ""),
                memory=arguments.get("memory", False),
                quiesce=False
            )
            return [types.TextContent(
                type="text",
                text=f"Snapshot '{arguments['snapshot_name']}' créé pour la VM '{arguments['vm_name']}'"
            )]
            
        else:
            return [types.TextContent(
                type="text",
                text=f"Outil inconnu: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de {name}: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Erreur: {str(e)}"
        )]
    finally:
        if manager:
            manager.disconnect()


def main():
    """Point d'entrée pour le package PyPI"""
    asyncio.run(main_async())

async def main_async():
    """Point d'entrée principal du serveur MCP"""
    logger.info("Démarrage du serveur MCP VMware")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    main()
