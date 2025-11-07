from typing import Dict

import os
import copy
import asyncio

from io import BytesIO

from aiosmb.commons.connection.factory import SMBConnectionFactory
from aiosmb.commons.interfaces.share import SMBShare
from aiosmb.commons.interfaces.machine import SMBMachine
from aiosmb.commons.interfaces.directory import SMBDirectory
from aiosmb.commons.interfaces.file import SMBFile
from aiosmb.wintypes.access_mask import FileAccessMask
from aiosmb.protocol.smb2.commands import (
    ShareAccess,
    CreateOptions,
    CreateDisposition
)

class FileServer:

    def __init__(
        self,
        host:str = 'localhost',
        port:str = '139',
        user_name:str = None,
        password:str = None,
    ):

        self.host = os.getenv('FILE_SERVER_HOST',host)
        self.port = os.getenv('FILE_SERVER_PORT',port)
        self.user_name = os.getenv('FILE_SERVER_USER',user_name)
        self.password = os.getenv('FILE_SERVER_PASSWORD',password)
        self.machine = None
        self.shares:Dict[str, SMBShare] = {}

    @property
    def url(self) -> str:
        return 'smb+ntlm-password://TEST\\{}:{}@{}:{}'.format(
            self.user_name,
            self.password,
            self.host,
            self.port
        )
    
    async def connect(self) -> None:
        
        self.connection  = SMBConnectionFactory.from_url(
            self.url
        ).get_connection(nosign=False)
        _, err = await self.connection.login()
        self.machine = SMBMachine(self.connection)

    async def disconnect(self) -> None:
        await self.machine.close()
        self.machine = None
        await self.connection.terminate()
        self.connection = None

    async def getShares(self) -> None:
        async for share, err in self.machine.list_shares():
            self.shares[share.name] = share

    async def connectShare(
        self,
        share_name:str,
    ) -> None:
        await self.shares[share_name].connect(self.connection)

    async def getParentDirectory(
        self,
        share_name:str,
        path:str
    ) -> SMBDirectory:
        
        directory_name_elements = []
        directory_name_ = copy.deepcopy(path)

        while directory_name_ != '/':
            directory_name_,name = os.path.split(directory_name_)
            directory_name_elements.append(name)

        directory_name_elements.reverse()

        parent_directory = self.shares[share_name].subdirs['']

        for index,directory_name_element in enumerate(directory_name_elements):
            async for entry, err in self.machine.list_directory(parent_directory):
                #no need to put here anything, the dir bject will store the refreshed data
                a = 1
            if index < len(directory_name_elements)-1:
                parent_directory = parent_directory.subdirs[directory_name_element]
    
        return parent_directory

    async def makeDirectory(
        self,
        share_name:str,
        directory_name:str,
        parent_directory:SMBDirectory
    ) ->None:        
        _, err = await self.machine.create_subdirectory(
            directory_name,
            parent_directory
        )

    async def readFile(
        self,
        file_name:str,
        path:str = None,
        parent_directory:SMBDirectory = None,
        share_name:str = 'Data'
    ) -> BytesIO:
        if parent_directory is None:
            parent_directory= await self.getParentDirectory(share_name,path)

        file_obj = parent_directory.files[file_name]

        data_buffer = BytesIO()
        async for data, err in self.machine.get_file_data(file_obj):
            if data is None:
                break
            data_buffer.write(data)

        data_buffer.seek(0)
        return data_buffer

    async def writeFile(
        self,
        file_name:str,
        data:BytesIO,
        path:str = None,
        parent_directory:SMBDirectory = None,
        share_name:str = 'Data'
    ) -> None:
        
        if parent_directory is None:
            parent_directory= await self.getParentDirectory(share_name,path)

        tree_entry, err = await self.connection.tree_connect(parent_directory.get_share_path())
        tree_id = tree_entry.tree_id
        newpath = '%s\\%s' % (parent_directory.fullpath, file_name)

        file_id,smb_reply,err = await self.connection.create(
            tree_id,
            newpath,
            FileAccessMask.GENERIC_READ | FileAccessMask.GENERIC_WRITE,
            ShareAccess.FILE_SHARE_READ | ShareAccess.FILE_SHARE_WRITE,
            CreateOptions.FILE_NON_DIRECTORY_FILE | CreateOptions.FILE_SYNCHRONOUS_IO_NONALERT,
            CreateDisposition.FILE_CREATE,
            0,
            return_reply = True
        )
        
        total_writen = 0
        position_in_file = 0
        
        while True:
            await asyncio.sleep(0) #to make sure we are not consuming all CPU
            chunk = data.read(self.connection.MaxWriteSize)
            if len(chunk) == 0:
                break
            
            bytes_written = await self.writeData(
                file_id,
                tree_id,
                chunk,
                position_in_file
            )
            position_in_file += bytes_written
            total_writen += bytes_written

        await self.connection.close(tree_id, file_id)
        
    async def writeData(
        self,
        file_id,
        tree_id,
        data,
        position_in_file
    ) -> None:

        remaining = len(data)
        total_bytes_written = 0
        offset = 0

        while remaining != 0:
            bytes_written, err = await self.connection.write(
                tree_id,
                file_id,
                data[offset:len(data)],
                offset = position_in_file + offset
            )
            total_bytes_written += bytes_written
            remaining -= bytes_written
            offset += bytes_written

        return total_bytes_written
    
    async def deleteDirectory(
        self,
        directory_name:str,
        path:str = None,
        parent_directory:SMBDirectory = None,
        share_name:str = 'Data'
    ) -> None:
        if parent_directory is None:
            parent_directory= await self.getParentDirectory(share_name,path)

        tree_entry, err = await self.connection.tree_connect(parent_directory.get_share_path())
        tree_id = tree_entry.tree_id

        remfile = parent_directory.subdirs[directory_name]

        desired_access = FileAccessMask.DELETE | FileAccessMask.FILE_READ_ATTRIBUTES
        share_mode = ShareAccess.FILE_SHARE_DELETE
        create_options = CreateOptions.FILE_DIRECTORY_FILE | CreateOptions.FILE_DELETE_ON_CLOSE 
        create_disposition = CreateDisposition.FILE_OPEN
        file_attrs = 0

        file_id, err = await self.connection.create(
            tree_id,
            remfile.fullpath,
            desired_access,
            share_mode,
            create_options,
            create_disposition,
            file_attrs,
            return_reply = False
        )
        await self.connection.close(tree_id, file_id)
        await self.connection.tree_disconnect(tree_id)
    
    async def getDirectoryElementsName(
        self,
        parent_directory:SMBDirectory,
        directory_name:str
    ) -> None:
        elements_name = []
        async for obj, otype, err in parent_directory.list_r(
            self.connection,
            depth = 1,
            maxentries = -1
        ):
            elements_name.append(obj.name)

        return elements_name
