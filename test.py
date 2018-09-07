class Nii2DicomInputSpec(TraitedSpec):
    in_file = File(mandatory=True, desc='input nifti file')
    reference_dicom = traits.List(mandatory=True, desc='original umap')
#     out_file = Directory(genfile=True, desc='the output dicom file')


class Nii2DicomOutputSpec(TraitedSpec):
    out_file = Directory(exists=True, desc='the output dicom file')


class Nii2Dicom(BaseInterface):
    """
    Creates two umaps in dicom format

    fully compatible with the UTE study:

    Attenuation Correction pipeline

    """

    input_spec = Nii2DicomInputSpec
    output_spec = Nii2DicomOutputSpec

    def _run_interface(self, runtime):
        dcms = self.inputs.reference_dicom
        to_remove = [x for x in dcms if '.dcm' not in x]
        if to_remove:
            for f in to_remove:
                dcms.remove(f)
        nifti_image = nib.load(self.inputs.in_file)
        nii_data = nifti_image.get_data()
        if len(dcms) != nii_data.shape[2]:
            raise Exception('Different number of nifti and dicom files '
                            'provided. Dicom to nifti conversion require the '
                            'same number of files in order to run. Please '
                            'check.')
        os.mkdir('nifti2dicom')
        _, basename, _ = split_filename(self.inputs.in_file)
        for i in range(nii_data.shape[2]):
            dcm = pydicom.read_file(dcms[i])
            nifti = nii_data[:, :, i]
            nifti = nifti.astype('uint16')
            dcm.pixel_array.setflags(write=True)
            dcm.pixel_array.flat[:] = nifti.flat[:]
            dcm.PixelData = dcm.pixel_array.T.tostring()
            dcm.save_as('nifti2dicom/{0}_vol{1}.dcm'
                        .format(basename, str(i).zfill(4)))

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['out_file'] = (
            os.getcwd()+'/nifti2dicom')
        return outputs

    def _gen_filename(self, name):
        if name == 'out_file':
            fname = self._gen_outfilename()
        else:
            assert False
        return fname

    def _gen_outfilename(self):
        if isdefined(self.inputs.out_file):
            fpath = self.inputs.out_file
        else:
            fname = (
                split_extension(os.path.basename(self.inputs.in_file))[0] +
                '_dicom')
            fpath = os.path.join(os.getcwd(), fname)
        return fpath
